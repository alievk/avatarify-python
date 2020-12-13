import face_alignment
from skimage.transform import resize
from skimage import img_as_ubyte
import numpy as np
import cv2


def extract_bbox(frame, fa, increase_area=0.1):
    frame_shape = frame.shape
    
    if max(frame.shape[0], frame.shape[1]) > 640:
        scale_factor =  max(frame.shape[0], frame.shape[1]) / 640.0
        frame = resize(frame, (int(frame.shape[0] / scale_factor), int(frame.shape[1] / scale_factor)))
        frame = img_as_ubyte(frame)
    else:
        scale_factor = 1
    frame = frame[..., :3]
    bboxes = fa.face_detector.detect_from_image(frame[..., ::-1])
    if len(bboxes) == 0:
        return []
    
#     assert len(bboxes) == 1
    bbox = np.array(bboxes)[0, :-1] * scale_factor
    
#     return bbox

    left, top, right, bot = bbox
    width = right - left
    height = bot - top

    #Computing aspect preserving bbox
    width_increase = max(increase_area, ((1 + 2 * increase_area) * height - width) / (2 * width))
    height_increase = max(increase_area, ((1 + 2 * increase_area) * width - height) / (2 * height))

    left = int(left - width_increase * width)
    top = int(top - height_increase * height)
    right = int(right + width_increase * width)
    bot = int(bot + height_increase * height)

    
#     top, bot, left, right = max(0, top), min(bot, frame_shape[0]), max(0, left), min(right, frame_shape[1])
    
    return left, top, right, bot


def make_coordinate_grid():
    X, Y = np.meshgrid(np.arange(256), np.arange(256))
    X = 2 * (X / 255) - 1
    Y = 2 * (Y / 255) - 1
    return np.stack([X, Y], axis=-1)


def make_overlay_mask():
    identity_grid = make_coordinate_grid()
    dist_to_edge_grid = ((np.abs(identity_grid) - np.array([[1, 1]], dtype=np.float32))**2).min(axis=-1)
    mask = (1 - np.exp(-100*dist_to_edge_grid)).reshape(256, 256)
    return mask


def overlay(background, head, offset):
    background = np.array(background)[..., :3]
    mask = make_overlay_mask()[:, :, np.newaxis]
    if head.shape[:2] != mask.shape[:2]:
        head = cv2.resize(head, (mask.shape[1], mask.shape[0]))
    background[offset[0]:offset[0]+head.shape[0], offset[1]:offset[1]+head.shape[1]] = \
        background[offset[0]:offset[0]+head.shape[0], offset[1]:offset[1]+head.shape[1]] * (1 - mask) + \
        np.array(head)[..., :3] * mask
    
    return background.astype(np.uint8)


