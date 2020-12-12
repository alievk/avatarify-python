import sys
import time
from collections import defaultdict

import numpy as np
import cv2


def log(*args, file=sys.stderr, **kwargs):
    time_str = f'{time.time():.6f}'
    print(f'[{time_str}]', *args, file=file, **kwargs)


def info(*args, file=sys.stdout, **kwargs):
    print(*args, file=file, **kwargs)


class Tee(object):
    def __init__(self, filename, mode='w', terminal=sys.stderr):
        self.file = open(filename, mode, buffering=1)
        self.terminal = terminal

    def __del__(self):
        self.file.close()

    def write(self, *args, **kwargs):
        log(*args, file=self.file, **kwargs)
        log(*args, file=self.terminal, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.write(*args, **kwargs)

    def flush(self):
        self.file.flush()


class Logger():
    def __init__(self, filename, verbose=True):
        self.tee = Tee(filename)
        self.verbose = verbose

    def __call__(self, *args, important=False, **kwargs):
        if not self.verbose and not important:
            return

        self.tee(*args, **kwargs)


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
        self.t = None
        self.t_init = time.time()

    def tic(self):
        self.t = time.time()

    def toc(self, total=False):
        if total:
            return (time.time() - self.t_init) * 1000

        assert self.t, 'You forgot to call tic()'
        return (time.time() - self.t) * 1000

    def tocp(self, str):
        t = self.toc()
        log(f"{str} took {t:.4f}ms")
        return t


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


def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


def crop(img, p=0.7, offset_x=0, offset_y=0):
    h, w = img.shape[:2]
    x = int(min(w, h) * p)
    l = (w - x) // 2
    r = w - l
    u = (h - x) // 2
    d = h - u

    offset_x = clamp(offset_x, -l, w - r)
    offset_y = clamp(offset_y, -u, h - d)

    l += offset_x
    r += offset_x
    u += offset_y
    d += offset_y

    return img[u:d, l:r], (offset_x, offset_y)


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
