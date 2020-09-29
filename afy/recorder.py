import cv2
import os
import time
import asyncio


class Recorder:
    def __init__(self, save_dir='./', fps=20, postfix=''):
        self.save_dir = save_dir
        self.fps = fps
        self.postfix = postfix
        self.frames = []

    def __del__(self):
        self.stop()

    def stop(self):
        if not self.frames:
            return

        if not os.path.isdir(self.save_dir):
            os.mkdir(self.save_dir)

        out_name = time.strftime(f'%m-%d_%H-%M-%S')
        if self.postfix:
            out_name += postfix
        out_path = os.path.join(self.save_dir, out_name + '.mp4')

        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        frame_size = self.frames[0].shape[1], self.frames[0].shape[0]
        writer = cv2.VideoWriter(out_path, fourcc, self.fps, frame_size)

        print(f'Saving record file...')

        for frame in self.frames:
            writer.write(frame)

        print(f'Saved file {out_path}')

        writer.release()

        self.frames = []

    def put_frame(self, frame):
        self.frames += [frame]


def overlay_rec(image):
    return cv2.circle(image.copy(), (10, 10), 10, (0, 0, 255), -1)


def main():
    cv2.namedWindow('src')

    cap = cv2.VideoCapture(0)
    recorder = Recorder(save_dir='records')
    recording = False
    record_task = None

    while True:
        ret, cam_frame = cap.read()

        cam_frame = cv2.resize(cam_frame, None, None, 0.5, 0.5)

        final_image = cam_frame.copy()

        key = cv2.waitKey(1)

        if key == 27: # ESC
            break
        elif key == ord('r'):
            if recording:
                recorder.stop()

            recording = not recording
        
        if recording:
            recorder.put_frame(final_image)

            final_image = overlay_rec(final_image)

        cv2.imshow('src', final_image)


if __name__ == '__main__':
    main()