from predictor_local import PredictorLocal
from arguments import opt
from networking import SerializingContext

from time import time

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
        self.context = SerializingContext()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.connect(f"tcp://{worker_host}:{worker_port}")
        print(f"Connected to {worker_host}:{worker_port}")
        self.predictor_args = (args, kwargs)
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

        s = time()
        if attr == 'predict':
            image = args[0]
            assert isinstance(image, np.ndarray), 'Expected image'
            print(image.dtype)
            ret_code, data = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
        else:
            data = pack_message((args, kwargs))
        print('PACK ', int((time() - s)*1000))

        s = time()
        self.socket.send_data(attr, data)
        print('SEND ', int((time() - s)*1000))

        s = time()
        attr_recv, data_recv = self.socket.recv_data()
        print('RECV ', int((time() - s)*1000))

        s = time()
        if attr_recv == 'predict':
            result = cv2.imdecode(np.frombuffer(data_recv, dtype='uint8'), -1)
        else:
            result = unpack_message(data_recv)
        print('UNPACK ', int((time() - s)*1000))

        return result


def message_handler(port):
    print("Creating socket")
    context = SerializingContext()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % port)
    predictor = None
    predictor_args = ()

    print("Listening for messages on port:", port)
    try:
        while True:
            s = time()
            ss = time()
            attr, data = socket.recv_data()
            print('RECV ', int((time() - ss)*1000))

            try:
                ss = time()
                if attr == 'predict':
                    image = cv2.imdecode(np.frombuffer(data, dtype='uint8'), -1)
                else:
                    args = unpack_message(data)
                print('UNPACK ', int((time() - ss)*1000))
            except ValueError:
                print("Invalid Message")
                continue

            ss = time()
            if attr == "__init__":
                if args == predictor_args:
                    print("Same config as before... reusing previous predictor")
                else:
                    del predictor
                    predictor_args = args
                    predictor = PredictorLocal(*predictor_args[0], **predictor_args[1])
                    print("Initialized predictor with:", predictor_args)
                result = True
            elif attr == 'predict':
                result = getattr(predictor, attr)(image)
            else:
                result = getattr(predictor, attr)(*args[0], **args[1])
            print('CALL ', int((time() - ss)*1000))

            ss = time()
            if attr == 'predict':
                assert isinstance(result, np.ndarray), 'Expected image'
                ret_code, data_send = cv2.imencode(".jpg", result, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
            else:
                data_send = pack_message(result)
            print('PACK ', int((time() - ss)*1000))

            ss = time()
            socket.send_data(attr, data_send)
            print('SEND ', int((time() - ss)*1000))

            print('CYCLE ', int((time() - s)*1000))
    except KeyboardInterrupt:
        pass

def run_worker(port):
    message_handler(port)
