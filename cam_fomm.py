import os, sys
import glob
import yaml
import time
import requests

import imageio
import numpy as np
from skimage.transform import resize
import cv2


from videocaptureasync import VideoCaptureAsync
import predictor_local
import predictor_remote
from arguments import opt

from sys import platform as _platform
_streaming = False
if _platform == 'linux' or _platform == 'linux2':
    import pyfakewebcam
    _streaming = True


def is_new_frame_better(source, driving, precitor):
    global avatar_kp
    global display_string
    
    if avatar_kp is None:
        display_string = "No face detected in avatar."
        return False
    
    if predictor.get_start_frame() is None:
        display_string = "No frame to compare to."
        return True
    
    driving_smaller = resize(driving, (128, 128))[..., :3]
    new_kp = predictor.get_frame_kp(driving)
    
    if new_kp is not None:
        new_norm = (np.abs(avatar_kp - new_kp) ** 2).sum()
        old_norm = (np.abs(avatar_kp - predictor.get_start_frame_kp()) ** 2).sum()
        
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
    pad = int(256 * (w / h) - 256)
    out = np.pad(img, [[0,0], [pad//2, pad//2], [0,0]], 'constant')
    out = cv2.resize(out, (w, h))
    return out


def load_stylegan_avatar():
    url = "https://thispersondoesnotexist.com/image"
    r = requests.get(url, headers={'User-Agent': "My User Agent 1.0"}).content

    image = np.frombuffer(r, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = resize(image, (256, 256))

    return image

def change_avatar(predictor, new_avatar):
    global avatar, avatar_kp
    avatar_kp = predictor.get_frame_kp(new_avatar)
    avatar = new_avatar

def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":

    global display_string
    display_string = ""

    if opt.no_stream:
        log('Force no streaming')
        _streaming = False

    log('Loading Predictor')
    if opt.is_worker:
        predictor_remote.run_worker(opt.worker_port)
        sys.exit(0)
    elif opt.worker_host:
        predictor = predictor_remote.PredictorRemote(
            worker_host=opt.worker_host, worker_port=opt.worker_port,
            config_path=opt.config, checkpoint_path=opt.checkpoint,
            relative=opt.relative, adapt_movement_scale=opt.adapt_scale
        )
    else:
        predictor = predictor_local.PredictorLocal(
            config_path=opt.config, checkpoint_path=opt.checkpoint,
            relative=opt.relative, adapt_movement_scale=opt.adapt_scale
        )

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
    
    # cap = cv2.VideoCapture(opt.cam)
    cap = VideoCaptureAsync(opt.cam)
    if not cap.isOpened():
        log("Cannot open camera. Try to choose other CAMID in './scripts/settings.sh'")
        exit()
    cap.start()

    ret, frame = cap.read()
    if not ret:
        log("Cannot read from camera")
        exit()

    if _streaming:
        stream = pyfakewebcam.FakeWebcam(f'/dev/video{opt.virt_cam}', frame.shape[1], frame.shape[0])

    cur_ava = 0    
    avatar = None
    change_avatar(predictor, avatars[cur_ava])
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
        t_start = time.time()

        green_overlay = False
        
        ret, frame = cap.read()
        if not ret:
            log("Can't receive frame (stream end?). Exiting ...")
            break

        frame_orig = frame.copy()

        frame, lrud = crop(frame, p=frame_proportion)
        frame = resize(frame, (256, 256))[..., :3]

        if find_keyframe:
            if is_new_frame_better(avatar, frame, predictor):
                log("Taking new frame!")
                green_overlay = True
                predictor.reset_frames()

        if opt.verbose:
            preproc_time = (time.time() - t_start) * 1000
            log(f'PREPROC: {preproc_time:.3f}ms')

        if passthrough:
            out = frame_orig[..., ::-1]
        else:
            pred_start = time.time()
            pred = predictor.predict(frame, avatar)
            out = pred
            pred_time = (time.time() - pred_start) * 1000
            if opt.verbose:
                log(f'PRED: {pred_time:.3f}ms')

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
            change_avatar(predictor, avatars[cur_ava])
        elif key == ord('a'):
            cur_ava -= 1
            if cur_ava < 0:
                cur_ava = len(avatars) - 1
            passthrough = False
            change_avatar(predictor, avatars[cur_ava])
        elif key == ord('w'):
            frame_proportion -= 0.05
            frame_proportion = max(frame_proportion, 0.1)
        elif key == ord('s'):
            frame_proportion += 0.05
            frame_proportion = min(frame_proportion, 1.0)
        elif key == ord('x'):
           predictor.reset_frames()
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
                change_avatar(predictor, avatar)
            except:
                log('Failed to load StyleGAN avatar')
        elif key == ord('i'):
            show_fps = not show_fps
        elif 48 < key < 58:
            cur_ava = min(key - 49, len(avatars) - 1)
            passthrough = False
            change_avatar(predictor, avatars[cur_ava])
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
            
        if find_keyframe:
            preview_frame = cv2.putText(preview_frame, display_string, (10, 220), 0, 0.5, (255, 255, 255), 1)

        if show_fps:
            fps_string = f'FPS: {fps:.2f}'
            preview_frame = cv2.putText(preview_frame, fps_string, (10, 240), 0, 0.5, (255, 255, 255), 1)

        cv2.imshow('cam', preview_frame)
        cv2.imshow('avatarify', out[..., ::-1])

        if opt.verbose:
            postproc_time = (time.time() - postproc_start) * 1000
            log(f'POSTPROC: {postproc_time:.3f}ms')

        fps_hist.append(time.time() - t_start)
        if len(fps_hist) == 10:
            fps = 10 / sum(fps_hist)
            fps_hist = []

    #cap.release()
    cap.stop()
    cv2.destroyAllWindows()
