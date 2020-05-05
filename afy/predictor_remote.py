from predictor_local import PredictorLocal
from arguments import opt

from time import time

import zmq
import imagezmq
import blosc
import msgpack
import msgpack_numpy as m
m.patch()


DEFAULT_PORT = 5556


if opt.compress:
    def pack_message(msg):
        return blosc.compress(msgpack.packb(msg), typesize=8)
    
    def unpack_message(msg):
        return msgpack.unpackb(blosc.decompress(msg))
else:
    def pack_message(msg):
        return msgpack.packb(msg)
    
    def unpack_message(msg):
        return msgpack.unpackb(msg)


class PredictorRemote:
    def __init__(self, *args, worker_host='localhost', worker_port=DEFAULT_PORT, **kwargs):
        self.worker_host = worker_host
        self.worker_port = worker_port
        self.context = zmq.Context()
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

    def __getattr__(self, item):
        return lambda *args, **kwargs: self._send_recv_msg((item, args, kwargs))

    def _send_recv_msg(self, msg):
        s = time()
        msg_pack = pack_message(msg)
        print('PACK ', int((time() - s)*1000))
        s = time()
        self.socket.send(msg_pack, copy=True)
        print('SEND ', int((time() - s)*1000))
        s = time()
        response = self.socket.recv()
        print('RECV ', int((time() - s)*1000))
        s = time()
        msg_recv = unpack_message(response)
        print('UNPACK ', int((time() - s)*1000))
        return msg_recv

from time import time

def message_handler(port):
    print("Creating socket")
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % port)
    predictor = None
    predictor_args = ()

    print("Listening for messages on port:", port)
    while True:
        s = time()
        ss = time()
        msg_raw = socket.recv()
        print('RECV ', int((time() - ss)*1000))
        try:
            ss = time()
            msg = unpack_message(msg_raw)
            print('UNPACK ', int((time() - ss)*1000))
        except ValueError:
            print("Invalid Message")
            continue
        method = msg[0]
        if method == "__init__":
            predictor_args_new = msg[1:]
            if predictor_args_new == predictor_args:
                print("Same config as before... reusing previous predictor")
            else:
                del predictor
                predictor_args = predictor_args_new
                predictor = PredictorLocal(*predictor_args[0], **predictor_args[1])
                print("Initialized predictor with:", predictor_args)
            result = True
        else:
            ss = time()
            result = getattr(predictor, method)(*msg[1], **msg[2])
            print('CALL ', int((time() - ss)*1000))
        ss = time()
        socket.send(pack_message(result), copy=True)
        print('SEND ', int((time() - ss)*1000))
        print('CYCLE ', int((time() - s)*1000))


def run_worker(port):
    message_handler(port)
