from predictor_local import PredictorLocal
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
JPEG_QUALITY = 95


def pack_message(msg):
    return msgpack.packb(msg)


def unpack_message(msg):
    return msgpack.unpackb(msg)


class PredictorRemote:
    def __init__(self, *args, worker_host='localhost', worker_port=DEFAULT_PORT, **kwargs):
        self.worker_host = worker_host
        self.worker_port = worker_port
        self.predictor_args = (args, kwargs)

        self.context = SerializingContext()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.connect(f"tcp://{worker_host}:{worker_port}")
        log(f"Connected to {worker_host}:{worker_port}")

        self.timing = AccumDict()

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
            ret_code, data = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
        else:
            data = pack_message((args, kwargs))
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
            result = unpack_message(data_recv)
        self.timing.add('UNPACK', tt.toc())

        Once(self.timing, per=1)

        return result


def message_handler(port):
    log("Creating socket")
    context = SerializingContext()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % port)
    log("Listening for messages on port:", port)

    predictor = None
    predictor_args = ()
    timing = AccumDict()
    
    try:
        while True:
            tt = TicToc()

            tt.tic()
            attr, data = socket.recv_data()
            timing.add('RECV', tt.toc())

            try:
                tt.tic()
                if attr == 'predict':
                    image = cv2.imdecode(np.frombuffer(data, dtype='uint8'), -1)
                else:
                    args = unpack_message(data)
                timing.add('UNPACK', tt.toc())
            except ValueError:
                log("Invalid Message")
                continue

            tt.tic()
            if attr == "__init__":
                if args == predictor_args:
                    log("Same config as before... reusing previous predictor")
                else:
                    del predictor
                    predictor_args = args
                    predictor = PredictorLocal(*predictor_args[0], **predictor_args[1])
                    log("Initialized predictor with:", predictor_args)
                result = True
                tt.tic() # don't account for init
            elif attr == 'predict':
                result = getattr(predictor, attr)(image)
            else:
                result = getattr(predictor, attr)(*args[0], **args[1])
            timing.add('CALL', tt.toc())

            tt.tic()
            if attr == 'predict':
                assert isinstance(result, np.ndarray), 'Expected image'
                ret_code, data_send = cv2.imencode(".jpg", result, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
            else:
                data_send = pack_message(result)
            timing.add('PACK', tt.toc())

            tt.tic()
            socket.send_data(attr, data_send)
            timing.add('SEND', tt.toc())

            Once(timing, per=1)
    except KeyboardInterrupt:
        pass

def run_worker(port):
    message_handler(port)
