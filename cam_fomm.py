import os, sys
import glob
import yaml
import time
from argparse import ArgumentParser

import imageio
import numpy as np
from skimage.transform import resize

import torch
from sync_batchnorm import DataParallelWithCallback

from modules.generator import OcclusionAwareGenerator
from modules.keypoint_detector import KPDetector
from animate import normalize_kp
from scipy.spatial import ConvexHull

import cv2

def load_checkpoints(config_path, checkpoint_path, device='cuda'):

    with open(config_path) as f:
        config = yaml.load(f)

    generator = OcclusionAwareGenerator(**config['model_params']['generator_params'],
                                        **config['model_params']['common_params'])
    generator.to(device)

    kp_detector = KPDetector(**config['model_params']['kp_detector_params'],
                             **config['model_params']['common_params'])
    kp_detector.to(device)

    checkpoint = torch.load(checkpoint_path, map_location=device)
    generator.load_state_dict(checkpoint['generator'])
    kp_detector.load_state_dict(checkpoint['kp_detector'])

    generator = DataParallelWithCallback(generator)
    kp_detector = DataParallelWithCallback(kp_detector)

    generator.eval()
    kp_detector.eval()
    
    return generator, kp_detector


def crop(img, p=0.7):
    h, w = img.shape[:2]
    x = int(min(w, h) * p)
    l = (w - x) // 2
    r = w - l
    u = (h - x) // 2
    d = h - u
    return img[u:d, l:r], (l,r,u,d)


def pad_img(img, orig):
    h, w = orig.shape[:2]
    pad = int(256 * (w / h) - 256)
    out = np.pad(img, [[0,0], [pad//2, pad//2], [0,0]], 'constant')
    out = cv2.resize(out, (w, h))
    return out


def predict(driving_frame, source_image, relative, adapt_movement_scale, device='cuda'):
    global kp_driving_initial

    with torch.no_grad():
        source = torch.tensor(source_image[np.newaxis].astype(np.float32)).permute(0, 3, 1, 2).to(device)
        driving_frame = torch.tensor(driving_frame[np.newaxis].astype(np.float32)).permute(0, 3, 1, 2).to(device)
        kp_source = kp_detector(source)

        if kp_driving_initial is None:
            kp_driving_initial = kp_detector(driving_frame)

        kp_driving = kp_detector(driving_frame)
        kp_norm = normalize_kp(kp_source=kp_source, kp_driving=kp_driving,
                            kp_driving_initial=kp_driving_initial, use_relative_movement=relative,
                            use_relative_jacobian=relative, adapt_movement_scale=adapt_movement_scale)
        out = generator(source, kp_source=kp_source, kp_driving=kp_norm)

        out = np.transpose(out['prediction'].data.cpu().numpy(), [0, 2, 3, 1])[0]
        out = out[..., ::-1]
        out = (np.clip(out, 0, 1) * 255).astype(np.uint8)

        return out


def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":

    global kp_driving_initial

    parser = ArgumentParser()
    parser.add_argument("--config", required=True, help="path to config")
    parser.add_argument("--checkpoint", default='vox-cpk.pth.tar', help="path to checkpoint to restore")

    parser.add_argument("--relative", dest="relative", action="store_true", help="use relative or absolute keypoint coordinates")
    parser.add_argument("--adapt_scale", dest="adapt_scale", action="store_true", help="adapt movement scale based on convex hull of keypoints")
    parser.add_argument("--no-pad", dest="no_pad", action="store_true", help="don't pad output image")

    parser.add_argument("--cam", type=int, default=0, help="Webcam device ID")
    parser.add_argument("--pipe", action="store_true", help="Output jpeg images into stdout")
    parser.add_argument("--debug", action="store_true", help="Print debug information")

    parser.add_argument("--avatars", default="./avatars", help="path to avatars directory")
 
    parser.set_defaults(relative=False)
    parser.set_defaults(adapt_scale=False)
    parser.set_defaults(no_pad=False)

    opt = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu' 

    avatars=[]
    images_list = sorted(glob.glob(f'{opt.avatars}/*'))
    for i, f in enumerate(images_list):
        if f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png'):
            log(f'{i}: {f}')
            img = imageio.imread(f)
            if img.ndim == 2:
                img = np.tile(img[..., None], [1, 1, 3])
            img = resize(img, (256, 256))[..., :3]
            avatars.append(img)
    
    log('load checkpoints..')
    
    generator, kp_detector = load_checkpoints(config_path=opt.config, checkpoint_path=opt.checkpoint, device=device)

    kp_driving_initial = None

    cap = cv2.VideoCapture(opt.cam)

    if not cap.isOpened():
        log("Cannot open camera")
        exit()

    cur_ava = 0
    passthrough = False

    cv2.namedWindow('cam', cv2.WINDOW_GUI_NORMAL)
    cv2.namedWindow('avatarify', cv2.WINDOW_GUI_NORMAL)
    cv2.moveWindow('cam', 0, 0)
    cv2.moveWindow('avatarify', 600, 0)

    frame_proportion = 0.9

    overlay_alpha = 0.2
    preview_flip = False
    output_flip = False

    while True:
        ret, frame = cap.read()
        if not ret:
            log("Can't receive frame (stream end?). Exiting ...")
            break

        frame_orig = frame.copy()

        frame, lrud = crop(frame, p=frame_proportion)
        frame = resize(frame, (256, 256))[..., :3]

        if passthrough:
            out = frame
        else:
            pred_start = time.time()
            pred = predict(frame, avatars[cur_ava], opt.relative, opt.adapt_scale, device=device)
            if not opt.no_pad:
                pred = pad_img(pred, frame_orig)
            out = pred
            pred_time = (time.time() - pred_start) * 1000
            if opt.debug:
                log(f'PRED: {pred_time:.3f}ms')
        
        key = cv2.waitKey(1)

        if key == ord('q'):
            break
        elif key == ord('d'):
            cur_ava += 1
            if cur_ava >= len(avatars):
                cur_ava = 0
            passthrough = False
        elif key == ord('a'):
            cur_ava -= 1
            if cur_ava < 0:
                cur_ava = len(avatars) - 1
            passthrough = False
        elif key == ord('w'):
            frame_proportion -= 0.05
            frame_proportion = max(frame_proportion, 0.1)
        elif key == ord('s'):
            frame_proportion += 0.05
            frame_proportion = min(frame_proportion, 1.0)
        elif key == ord('x'):
           kp_driving_initial = None
        elif key == ord('z'):
            overlay_alpha = max(overlay_alpha - 0.1, 0.0)
        elif key == ord('c'):
            overlay_alpha = min(overlay_alpha + 0.1, 1.0)
        elif key == ord('r'):
            preview_flip = not preview_flip
        elif key == ord('t'):
            output_flip = not output_flip
        elif 48 < key < 58:
            cur_ava = min(key - 49, len(avatars) - 1)
            passthrough = False
        elif key == 48:
            passthrough = not passthrough
        elif key != -1 and not opt.pipe:
            log(key)

        if opt.pipe:
            buf = cv2.imencode('.jpg', out)[1].tobytes()
            sys.stdout.buffer.write(buf)

        preview_frame = cv2.addWeighted( avatars[cur_ava][:,:,::-1], overlay_alpha, frame, 1.0 - overlay_alpha, 0.0)
        
        if preview_flip:
            preview_frame = cv2.flip(preview_frame, 1)
            
        if output_flip:
            out = cv2.flip(out, 1)

        cv2.imshow('cam', preview_frame)
        cv2.imshow('avatarify', out)

    cap.release()
    cv2.destroyAllWindows()
