from arguments import opt
from networking import SerializingContext, check_connection
from utils import log, TicToc, AccumDict, Once

import cv2
import numpy as np
import zmq
import msgpack
import msgpack_numpy as m
m.patch()


class PredictorRemote:
    def __init__(self, *args, bind_port=None, connect_address=None, **kwargs):
        self.bind_port = bind_port
        self.connect_address = connect_address
        self.predictor_args = (args, kwargs)
        self.timing = AccumDict()

        self.context = SerializingContext()
        self.socket = self.context.socket(zmq.PAIR)

        if self.bind_port is None:
            if not self.connect_address.startswith("tcp://"):
                self.connect_address = "tcp://" + self.connect_address
            log(f"Connecting to {self.connect_address}")
            self.socket.connect(self.connect_address)

            if not check_connection(self.socket):
                self.socket.disconnect(self.connect_address)
                raise ConnectionError(f"Could not connect to {self.connect_address}")

            log(f"Connected to {self.connect_address}")
        else:
            self.socket.bind(f"tcp://*:%s" % self.bind_port)
            log(f"Listening on port {self.bind_port}")

        self.init_worker()

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
