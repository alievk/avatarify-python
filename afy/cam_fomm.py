import os, sys
from sys import platform as _platform
import glob
import yaml
import time
import requests

import numpy as np
import cv2

from afy.videocaptureasync import VideoCaptureAsync
from afy.arguments import opt
from afy.utils import info, Once, Tee, crop, pad_img, resize, TicToc
import afy.camera_selector as cam_selector


log = Tee('./var/log/cam_fomm.log')


if _platform == 'darwin':
    if not opt.is_client:
        info('\nOnly remote GPU mode is supported for Mac (use --is-client and --connect options to connect to the server)')
        info('Standalone version will be available lately!\n')
        exit()


def is_new_frame_better(source, driving, predictor):
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


def load_stylegan_avatar():
    url = "https://thispersondoesnotexist.com/image"
    r = requests.get(url, headers={'User-Agent': "My User Agent 1.0"}).content

    image = np.frombuffer(r, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = resize(image, (IMG_SIZE, IMG_SIZE))

    return image

def load_images(IMG_SIZE = 256):
    avatars = []
    filenames = []
    images_list = sorted(glob.glob(f'{opt.avatars}/*'))
    for i, f in enumerate(images_list):
        if f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png'):
            img = cv2.imread(f)
            if img.ndim == 2:
                img = np.tile(img[..., None], [1, 1, 3])
            img = img[..., :3][..., ::-1]
            img = resize(img, (IMG_SIZE, IMG_SIZE))
            avatars.append(img)
            filenames.append(f)
    return avatars, filenames

def change_avatar(predictor, new_avatar):
    global avatar, avatar_kp, kp_source
    avatar_kp = predictor.get_frame_kp(new_avatar)
    kp_source = None
    avatar = new_avatar
    predictor.set_source_image(avatar)


def draw_rect(img, rw=0.6, rh=0.8, color=(255, 0, 0), thickness=2):
    h, w = img.shape[:2]
    l = w * (1 - rw) // 2
    r = w - l
    u = h * (1 - rh) // 2
    d = h - u
    img = cv2.rectangle(img, (int(l), int(u)), (int(r), int(d)), color, thickness)


def print_help():
    info('\n\n=== Control keys ===')
    info('1-9: Change avatar')
    for i, fname in enumerate(avatar_names):
        key = i + 1
        name = fname.split('/')[-1]
        info(f'{key}: {name}')
    info('W: Zoom camera in')
    info('S: Zoom camera out')
    info('A: Previous avatar in folder')
    info('D: Next avatar in folder')
    info('Q: Get random avatar')
    info('X: Calibrate face pose')
    info('I: Show FPS')
    info('ESC: Quit')
    info('\nFull key list: https://github.com/alievk/avatarify#controls')
    info('\n\n')


def draw_fps(frame, fps, timing, x0=10, y0=20, ystep=30, fontsz=0.5, color=(255, 255, 255)):
    frame = frame.copy()
    cv2.putText(frame, f"FPS: {fps:.1f}", (x0, y0 + ystep * 0), 0, fontsz * IMG_SIZE / 256, color, 1)
    cv2.putText(frame, f"Model time (ms): {timing['predict']:.1f}", (x0, y0 + ystep * 1), 0, fontsz * IMG_SIZE / 256, color, 1)
    cv2.putText(frame, f"Preproc time (ms): {timing['preproc']:.1f}", (x0, y0 + ystep * 2), 0, fontsz * IMG_SIZE / 256, color, 1)
    cv2.putText(frame, f"Postproc time (ms): {timing['postproc']:.1f}", (x0, y0 + ystep * 3), 0, fontsz * IMG_SIZE / 256, color, 1)
    return frame


def draw_calib_text(frame, thk=2, fontsz=0.5, color=(0, 0, 255)):
    frame = frame.copy()
    cv2.putText(frame, "FIT FACE IN RECTANGLE", (40, 20), 0, fontsz * IMG_SIZE / 255, color, thk)
    cv2.putText(frame, "W - ZOOM IN", (60, 40), 0, fontsz * IMG_SIZE / 255, color, thk)
    cv2.putText(frame, "S - ZOOM OUT", (60, 60), 0, fontsz * IMG_SIZE / 255, color, thk)
    cv2.putText(frame, "THEN PRESS X", (60, 245), 0, fontsz * IMG_SIZE / 255, color, thk)
    return frame


def select_camera(config):
    cam_config = config['cam_config']
    cam_id = None

    if os.path.isfile(cam_config):
        with open(cam_config, 'r') as f:
            cam_config = yaml.load(f, Loader=yaml.FullLoader)
            cam_id = cam_config['cam_id']
    else:
        cam_frames = cam_selector.query_cameras(config['query_n_cams'])

        if cam_frames:
            cam_id = cam_selector.select_camera(cam_frames, window="CLICK ON YOUR CAMERA")
            log(f"Selected camera {cam_id}")

            with open(cam_config, 'w') as f:
                yaml.dump({'cam_id': cam_id}, f)
        else:
            log("No cameras are available")

    return cam_id


if __name__ == "__main__":
    with open('config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    global display_string
    display_string = ""

    IMG_SIZE = 256

    log('Loading Predictor')
    predictor_args = {
        'config_path': opt.config,
        'checkpoint_path': opt.checkpoint,
        'relative': opt.relative,
        'adapt_movement_scale': opt.adapt_scale,
        'enc_downscale': opt.enc_downscale
    }
    if opt.is_worker:
        from afy import predictor_worker
        predictor_worker.run_worker(opt.in_port, opt.out_port)
        sys.exit(0)
    elif opt.is_client:
        from afy import predictor_remote
        try:
            predictor = predictor_remote.PredictorRemote(
                in_addr=opt.in_addr, out_addr=opt.out_addr,
                **predictor_args
            )
        except ConnectionError as err:
            log(err)
            sys.exit(1)
        predictor.start()
    else:
        from afy import predictor_local
        predictor = predictor_local.PredictorLocal(
            **predictor_args
        )

    cam_id = select_camera(config)

    if cam_id is None:
        exit(1)

    cap = VideoCaptureAsync(cam_id)
    cap.start()

    avatars, avatar_names = load_images()

    enable_vcam = not opt.no_stream

    ret, frame = cap.read()
    stream_img_size = frame.shape[1], frame.shape[0]

    if enable_vcam:
        if _platform in ['linux', 'linux2']:
            try:
                import pyfakewebcam
            except ImportError:
                log("pyfakewebcam is not installed.")
                exit(1)

            stream = pyfakewebcam.FakeWebcam(f'/dev/video{opt.virt_cam}', *stream_img_size)
        else:
            enable_vcam = False
            # log("Virtual camera is supported only on Linux.")
        
        # if not enable_vcam:
            # log("Virtual camera streaming will be disabled.")

    cur_ava = 0    
    avatar = None
    change_avatar(predictor, avatars[cur_ava])
    passthrough = False

    cv2.namedWindow('cam', cv2.WINDOW_GUI_NORMAL)
    cv2.moveWindow('cam', 500, 250)

    frame_proportion = 0.9
    frame_offset_x = 0
    frame_offset_y = 0

    overlay_alpha = 0.0
    preview_flip = False
    output_flip = False
    find_keyframe = False
    is_calibrated = False

    fps_hist = []
    fps = 0
    show_fps = False

    print_help()

    try:
        while True:
            tt = TicToc()

            timing = {
                'preproc': 0,
                'predict': 0,
                'postproc': 0
            }

            green_overlay = False

            tt.tic()

            ret, frame = cap.read()
            if not ret:
                log("Can't receive frame (stream end?). Exiting ...")
                break

            frame = frame[..., ::-1]
            frame_orig = frame.copy()

            frame, lrudwh = crop(frame, p=frame_proportion, offset_x=frame_offset_x, offset_y=frame_offset_y)
            frame_lrudwh = lrudwh
            frame = resize(frame, (IMG_SIZE, IMG_SIZE))[..., :3]

            if find_keyframe:
                if is_new_frame_better(avatar, frame, predictor):
                    log("Taking new frame!")
                    green_overlay = True
                    predictor.reset_frames()

            timing['preproc'] = tt.toc()

            if passthrough:
                out = frame
            elif is_calibrated:
                tt.tic()
                out = predictor.predict(frame)
                if out is None:
                    log('predict returned None')
                timing['predict'] = tt.toc()
            else:
                out = None

            tt.tic()
            
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
            elif key == ord('H'):
                if frame_lrudwh[0] - 1 > 0:
                    frame_offset_x -= 1
            elif key == ord('h'):
                if frame_lrudwh[0] - 5 > 0:
                    frame_offset_x -= 5
            elif key == ord('K'):
                if frame_lrudwh[1] + 1 < frame_lrudwh[4]:
                    frame_offset_x += 1
            elif key == ord('k'):
                if frame_lrudwh[1] + 5 < frame_lrudwh[4]:
                    frame_offset_x += 5
            elif key == ord('J'):
                if frame_lrudwh[2] - 1 > 0:
                    frame_offset_y -= 1
            elif key == ord('j'):
                if frame_lrudwh[2] - 5 > 0:
                    frame_offset_y -= 5
            elif key == ord('U'):
                if frame_lrudwh[3] + 1 < frame_lrudwh[5]:
                    frame_offset_y += 1
            elif key == ord('u'):
                if frame_lrudwh[3] + 5 < frame_lrudwh[5]:
                    frame_offset_y += 5
            elif key == ord('Z'):
                frame_offset_x = 0
                frame_offset_y = 0
                frame_proportion = 0.9
            elif key == ord('x'):
                predictor.reset_frames()

                if not is_calibrated:
                    cv2.namedWindow('avatarify', cv2.WINDOW_GUI_NORMAL)
                    cv2.moveWindow('avatarify', 600, 250)
                
                is_calibrated = True
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
            elif key == ord('l'):
                try:
                    log('Reloading avatars...')
                    avatars, avatar_names = load_images()
                    passthrough = False
                    log("Images reloaded")
                except:
                    log('Image reload failed')
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

            if overlay_alpha > 0:
                preview_frame = cv2.addWeighted( avatars[cur_ava], overlay_alpha, frame, 1.0 - overlay_alpha, 0.0)
            else:
                preview_frame = frame.copy()
            
            if preview_flip:
                preview_frame = cv2.flip(preview_frame, 1)
                
            if green_overlay:
                green_alpha = 0.8
                overlay = preview_frame.copy()
                overlay[:] = (0, 255, 0)
                preview_frame = cv2.addWeighted( preview_frame, green_alpha, overlay, 1.0 - green_alpha, 0.0)

            timing['postproc'] = tt.toc()
                
            if find_keyframe:
                preview_frame = cv2.putText(preview_frame, display_string, (10, 220), 0, 0.5 * IMG_SIZE / 256, (255, 255, 255), 1)

            if show_fps:
                preview_frame = draw_fps(preview_frame, fps, timing)

            if not is_calibrated:
                preview_frame = draw_calib_text(preview_frame)

            if not opt.hide_rect:
                draw_rect(preview_frame)

            cv2.imshow('cam', preview_frame[..., ::-1])

            if out is not None:
                if not opt.no_pad:
                    out = pad_img(out, stream_img_size)

                if output_flip:
                    out = cv2.flip(out, 1)

                if enable_vcam:
                    out = resize(out, stream_img_size)
                    stream.schedule_frame(out)

                cv2.imshow('avatarify', out[..., ::-1])

            fps_hist.append(tt.toc(total=True))
            if len(fps_hist) == 10:
                fps = 10 / (sum(fps_hist) / 1000)
                fps_hist = []
    except KeyboardInterrupt:
        log("main: user interrupt")

    log("stopping camera")
    cap.stop()

    cv2.destroyAllWindows()

    if opt.is_client:
        log("stopping remote predictor")
        predictor.stop()

    log("main: exit")
