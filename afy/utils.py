import sys
import time
from collections import defaultdict

import numpy as np
import cv2


def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Once():
    _id = {}

    def __init__(self, what, who=log, per=1e12):
        """ Do who(what) once per seconds.
        what: args for who
        who: callable
        per: frequency in seconds.
        """
        assert callable(who)
        now = time.time()
        if what not in Once._id or now - Once._id[what] > per:
            who(what)
            Once._id[what] = now


class TicToc:
    def __init__(self):
        self.tic_toc_tic = None

    def tic(self):
        self.tic_toc_tic = time.time()

    def toc(self):
        assert self.tic_toc_tic, 'You forgot to call tic()'
        return (time.time() - self.tic_toc_tic) * 1000

    def tocp(self, str):
        log(f"{str} took {toc():.4f}ms")

    @staticmethod
    def print(name=''):
        log(f'\n=== {name} Timimg ===')
        for fn, times in self.timing.items():
            min, max, mean, p95 = np.min(times), np.max(times), np.mean(times), np.percentile(times, 95)
            log(f'{fn}:\tmin: {min:.4f}\tmax: {max:.4f}\tmean: {mean:.4f}ms\tp95: {p95:.4f}ms')


class AccumDict:
    def __init__(self, num_f=3):
        self.d = defaultdict(list)
        self.num_f = num_f
        
    def add(self, k, v):
        self.d[k] += [v]
        
    def __dict__(self):
        return self.d

    def __getitem__(self, key):
        return self.d[key]
    
    def __str__(self):
        s = ''
        for k in self.d:
            if not self.d[k]:
                continue
            cur = self.d[k][-1]
            avg = np.mean(self.d[k])
            format_str = '{:.%df}' % self.num_f
            cur_str = format_str.format(cur)
            avg_str = format_str.format(avg)
            s += f'{k} {cur_str} ({avg_str})\t\t'
        return s
    
    def __repr__(self):
        return self.__str__()


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
    return cv2.resize(img, size)
