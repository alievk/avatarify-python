from arguments import opt
from networking import SerializingContext
from utils import log, TicToc, AccumDict, Once

import cv2
import numpy as np
import zmq
import msgpack
import msgpack_numpy as m
m.patch()


DEFAULT_PORT = 5556


class PredictorRemote:
    def __init__(self, *args, worker_host='localhost', worker_port=DEFAULT_PORT, **kwargs):
        self.worker_host = worker_host
        self.worker_port = worker_port
        self.predictor_args = (args, kwargs)
        self.timing = AccumDict()

        self.address = f"tcp://{worker_host}:{worker_port}"
        self.context = SerializingContext()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.connect(self.address)

        if not self.check_connection():
            self.socket.disconnect(self.address)
            # TODO: this hangs, as well as context.__del__
            # self.context.destroy()
            raise ConnectionError(f"Could not connect to {worker_host}:{worker_port}")

        log(f"Connected to {self.address}")

        self.init_worker()

    def check_connection(self, timeout=1000):
        msg = (
            'hello',
            [], {}
        )

        try:
            old_rcvtimeo = self.socket.RCVTIMEO
            self.socket.RCVTIMEO = timeout
            response = self._send_recv_msg(msg)
            self.socket.RCVTIMEO = old_rcvtimeo
        except zmq.error.Again:
            return False

        return response == 'OK'

    def init_worker(self):
        msg = (
            '__init__',
            *self.predictor_args,
        )
        return self._send_recv_msg(msg)

    def __getattr__(self, attr):
        return lambda *args, **kwargs: self._send_recv_msg((attr, args, kwargs))

    def _send_recv_msg(self, msg):
        attr, args, kwargs = msg

        tt = TicToc()
        tt.tic()
        if attr == 'predict':
            image = args[0]
            assert isinstance(image, np.ndarray), 'Expected image'
            ret_code, data = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), opt.jpg_quality])
        else:
            data = msgpack.packb((args, kwargs))
        self.timing.add('PACK', tt.toc())

        tt.tic()
        self.socket.send_data(attr, data)
        self.timing.add('SEND', tt.toc())

        tt.tic()
        attr_recv, data_recv = self.socket.recv_data()
        self.timing.add('RECV', tt.toc())

        tt.tic()
        if attr_recv == 'predict':
            result = cv2.imdecode(np.frombuffer(data_recv, dtype='uint8'), -1)
        else:
            result = msgpack.unpackb(data_recv)
        self.timing.add('UNPACK', tt.toc())

        Once(self.timing, per=1)

        return result
