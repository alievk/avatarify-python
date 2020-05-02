import sys

import numpy as np
import cv2
import skimage.transform


class Once():
    _id = []

    def __init__(self, what):
        if what not in Once._id:
            log(what)
            Once._id.append(what)


def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def crop(img, p=0.7, offset_x=0, offset_y=0):
    h, w = img.shape[:2]
    x = int(min(w, h) * p)
    l = (w - x) // 2
    r = w - l
    u = (h - x) // 2
    d = h - u
    l += offset_x
    r += offset_x
    u += offset_y
    d += offset_y

    return img[u:d, l:r], (l,r,u,d,w,h)


def pad_img(img, target_size, default_pad=0):
    sh, sw = img.shape[:2]
    w, h = target_size
    pad_w, pad_h = default_pad, default_pad
    if w / h > 1:
        pad_w += int(sw * (w / h) - sw) // 2
    else:
        pad_h += int(sh * (h / w) - sh) // 2
    out = np.pad(img, [[pad_h, pad_h], [pad_w, pad_w], [0,0]], 'constant')
    return out


def resize(img, size, version='cv'):
    if version == 'cv':
        return cv2.resize(img, size) / 255
    else:
        return skimage.transform.resize(img, size)
