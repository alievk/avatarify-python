import os, sys
import glob
import yaml
import time
from argparse import ArgumentParser
import requests

import imageio
import numpy as np
import skimage.transform
import cv2

import torch
from sync_batchnorm import DataParallelWithCallback

from modules.generator import OcclusionAwareGenerator
from modules.keypoint_detector import KPDetector
from animate import normalize_kp
from scipy.spatial import ConvexHull

import face_alignment

from videocaptureasync import VideoCaptureAsync

from sys import platform as _platform
_streaming = False
if _platform == 'linux' or _platform == 'linux2':
    import pyfakewebcam
    _streaming = True


def load_checkpoints(config_path, checkpoint_path, device='cuda'):

    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

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

def normalize_alignment_kp(kp):
    kp = kp - kp.mean(axis=0, keepdims=True)
    area = ConvexHull(kp[:, :2]).volume
    area = np.sqrt(area)
    kp[:, :2] = kp[:, :2] / area
    return kp
    
def get_frame_kp(fa, image):
    kp_landmarks = fa.get_landmarks(255 * image)
    if kp_landmarks:
        kp_image = kp_landmarks[0]
        kp_image = normalize_alignment_kp(kp_image)
        
        return kp_image
    else:
        return None

def is_new_frame_better(fa, source, driving, device):
    global start_frame
    global start_frame_kp
    global avatar_kp
    global display_string
    
    if avatar_kp is None:
        display_string = "No face detected in avatar."
        return False
    
    if start_frame is None:
        display_string = "No frame to compare to."
        return True
    
    driving_smaller = resize(driving, (128, 128))[..., :3]
    new_kp = get_frame_kp(fa, driving)
    
    if new_kp is not None:
        new_norm = (np.abs(avatar_kp - new_kp) ** 2).sum()
        old_norm = (np.abs(avatar_kp - start_frame_kp) ** 2).sum()
        
        out_string = "{0} : {1}".format(int(new_norm * 100), int(old_norm * 100))
        display_string = out_string
        log(out_string)
        
        return new_norm < old_norm
    else:
        display_string = "No face found!"
        return False

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
    pad = int(IMG_SIZE * (w / h) - IMG_SIZE)
    out = np.pad(img, [[0,0], [pad//2, pad//2], [0,0]], 'constant')
    out = cv2.resize(out, (w, h))
    return out


def resize(img, size, version='cv'):
    if version == 'cv':
        return cv2.resize(img, size) / 255
    else:
        return skimage.transform.resize(img, size)


def predict(driving_frame, source_image, relative, adapt_movement_scale, fa, device='cuda'):
    global start_frame
    global start_frame_kp
    global kp_driving_initial

    with torch.no_grad():
        source = torch.tensor(source_image[np.newaxis].astype(np.float32)).permute(0, 3, 1, 2).to(device)
        driving = torch.tensor(driving_frame[np.newaxis].astype(np.float32)).permute(0, 3, 1, 2).to(device)

        if kp_driving_initial is None:
            kp_driving_initial = kp_detector(driving)
            start_frame = driving_frame.copy()
            start_frame_kp = get_frame_kp(fa, driving_frame)

        kp_driving = kp_detector(driving)
        kp_norm = normalize_kp(kp_source=kp_source, kp_driving=kp_driving,
                            kp_driving_initial=kp_driving_initial, use_relative_movement=relative,
                            use_relative_jacobian=relative, adapt_movement_scale=adapt_movement_scale)
        out = generator(source, kp_source=kp_source, kp_driving=kp_norm)

        out = np.transpose(out['prediction'].data.cpu().numpy(), [0, 2, 3, 1])[0]
        out = (np.clip(out, 0, 1) * 255).astype(np.uint8)

        return out


def load_stylegan_avatar():
    url = "https://thispersondoesnotexist.com/image"
    r = requests.get(url, headers={'User-Agent': "My User Agent 1.0"}).content

    image = np.frombuffer(r, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = resize(image, (IMG_SIZE, IMG_SIZE))

    return image

def change_avatar(fa, new_avatar):
    global avatar, avatar_kp, kp_source
    avatar_kp = get_frame_kp(fa, new_avatar)
    kp_source = kp_detector(torch.tensor(new_avatar[np.newaxis].astype(np.float32)).permute(0, 3, 1, 2).to(device))
    avatar = new_avatar

def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":

    global display_string
    display_string = ""
    global kp_driving_initial
    kp_driving_initial = None
    global kp_source
    kp_source = None

    parser = ArgumentParser()
    parser.add_argument("--config", required=True, help="path to config")
    parser.add_argument("--checkpoint", default='vox-cpk.pth.tar', help="path to checkpoint to restore")

    parser.add_argument("--relative", dest="relative", action="store_true", help="use relative or absolute keypoint coordinates")
    parser.add_argument("--adapt_scale", dest="adapt_scale", action="store_true", help="adapt movement scale based on convex hull of keypoints")
    parser.add_argument("--no-pad", dest="no_pad", action="store_true", help="don't pad output image")

    parser.add_argument("--cam", type=int, default=0, help="Webcam device ID")
    parser.add_argument("--virt-cam", type=int, default=0, help="Virtualcam device ID")
    parser.add_argument("--no-stream", action="store_true", help="On Linux, force no streaming")

    parser.add_argument("--verbose", action="store_true", help="Print additional information")

    parser.add_argument("--avatars", default="./avatars", help="path to avatars directory")
 
    parser.set_defaults(relative=False)
    parser.set_defaults(adapt_scale=False)
    parser.set_defaults(no_pad=False)

    opt = parser.parse_args()

    IMG_SIZE = 256

    if opt.no_stream:
        log('Force no streaming')
        _streaming = False

    device = 'cuda' if torch.cuda.is_available() else 'cpu' 

    avatars=[]
    images_list = sorted(glob.glob(f'{opt.avatars}/*'))
    for i, f in enumerate(images_list):
        if f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png'):
            log(f'{i}: {f}')
            img = imageio.imread(f)
            if img.ndim == 2:
                img = np.tile(img[..., None], [1, 1, 3])
            img = resize(img, (IMG_SIZE, IMG_SIZE))[..., :3]
            avatars.append(img)
    
    log('load checkpoints..')
    
    generator, kp_detector = load_checkpoints(config_path=opt.config, checkpoint_path=opt.checkpoint, device=device)
    
    fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=True, device=device)

    cap = VideoCaptureAsync(opt.cam)
    cap.start()

    if _streaming:
        ret, frame = cap.read()
        stream = pyfakewebcam.FakeWebcam(f'/dev/video{opt.virt_cam}', frame.shape[1], frame.shape[0])

    cur_ava = 0    
    avatar = None
    change_avatar(fa, avatars[cur_ava])
    passthrough = False

    cv2.namedWindow('cam', cv2.WINDOW_GUI_NORMAL)
    cv2.namedWindow('avatarify', cv2.WINDOW_GUI_NORMAL)
    cv2.moveWindow('cam', 0, 0)
    cv2.moveWindow('avatarify', 600, 0)

    frame_proportion = 0.9

    overlay_alpha = 0.0
    preview_flip = False
    output_flip = False
    find_keyframe = False

    fps_hist = []
    fps = 0
    show_fps = False

    while True:
        timing = {
            'preproc': 0,
            'predict': 0,
            'postproc': 0
        }

        t_start = time.time()

        green_overlay = False
        
        ret, frame = cap.read()
        if not ret:
            log("Can't receive frame (stream end?). Exiting ...")
            break

        frame_orig = frame.copy()

        frame, lrud = crop(frame, p=frame_proportion)
        frame = resize(frame, (IMG_SIZE, IMG_SIZE))[..., :3]

        if find_keyframe:
            if is_new_frame_better(fa, avatar, frame, device):
                log("Taking new frame!")
                green_overlay = True
                kp_driving_initial = None

        timing['preproc'] = (time.time() - t_start) * 1000

        if passthrough:
            out = frame_orig[..., ::-1]
        else:
            pred_start = time.time()
            pred = predict(frame, avatar, opt.relative, opt.adapt_scale, fa, device=device)
            out = pred
            timing['predict'] = (time.time() - pred_start) * 1000

        postproc_start = time.time()

        if not opt.no_pad:
            out = pad_img(out, frame_orig)

        if out.dtype != np.uint8:
            out = (out * 255).astype(np.uint8)
        
        key = cv2.waitKey(1)

        if key == 27: # ESC
            break
        elif key == ord('d'):
            cur_ava += 1
            if cur_ava >= len(avatars):
                cur_ava = 0
            passthrough = False
            change_avatar(fa, avatars[cur_ava])
        elif key == ord('a'):
            cur_ava -= 1
            if cur_ava < 0:
                cur_ava = len(avatars) - 1
            passthrough = False
            change_avatar(fa, avatars[cur_ava])
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
        elif key == ord('f'):
            find_keyframe = not find_keyframe
        elif key == ord('q'):
            try:
                log('Loading StyleGAN avatar...')
                avatar = load_stylegan_avatar()
                passthrough = False
                change_avatar(fa, avatar)
            except:
                log('Failed to load StyleGAN avatar')
        elif key == ord('i'):
            show_fps = not show_fps
        elif 48 < key < 58:
            cur_ava = min(key - 49, len(avatars) - 1)
            passthrough = False
            change_avatar(fa, avatars[cur_ava])
        elif key == 48:
            passthrough = not passthrough
        elif key != -1:
            log(key)

        if _streaming:
            stream.schedule_frame(out)

        preview_frame = cv2.addWeighted( avatars[cur_ava][:,:,::-1], overlay_alpha, frame, 1.0 - overlay_alpha, 0.0)
        
        if preview_flip:
            preview_frame = cv2.flip(preview_frame, 1)
            
        if output_flip:
            out = cv2.flip(out, 1)
            
        if green_overlay:
            green_alpha = 0.8
            overlay = preview_frame.copy()
            overlay[:] = (0, 255, 0)
            preview_frame = cv2.addWeighted( preview_frame, green_alpha, overlay, 1.0 - green_alpha, 0.0)

        timing['postproc'] = (time.time() - postproc_start) * 1000
            
        if find_keyframe:
            preview_frame = cv2.putText(preview_frame, display_string, (10, 220), 0, 0.5 * IMG_SIZE / 256, (255, 255, 255), 1)

        if show_fps:
            timing_string = f"FPS/Model/Pre/Post: {fps:.1f} / {timing['predict']:.1f} / {timing['preproc']:.1f} / {timing['postproc']:.1f}"
            preview_frame = cv2.putText(preview_frame, timing_string, (10, 240), 0, 0.3 * IMG_SIZE / 256, (255, 255, 255), 1)

        cv2.imshow('cam', preview_frame)
        cv2.imshow('avatarify', out[..., ::-1])

        fps_hist.append(time.time() - t_start)
        if len(fps_hist) == 10:
            fps = 10 / sum(fps_hist)
            fps_hist = []

    cap.stop()
    cv2.destroyAllWindows()
