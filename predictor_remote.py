from predictor_local import PredictorLocal
from arguments import opt

import zmq
import msgpack
import msgpack_numpy as m
m.patch()


DEFAULT_PORT = 5556


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
        self.socket.send(msgpack.packb(msg), copy=False)
        response = self.socket.recv()
        return msgpack.unpackb(response)


def message_handler(port):
    print("Creating socket")
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % port)
    predictor = None
    predictor_args = ()

    print("Listening for messages on port:", port)
    while True:
        msg_raw = socket.recv()
        try:
            msg = msgpack.unpackb(msg_raw)
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
            result = getattr(predictor, method)(*msg[1], **msg[2])
        socket.send(msgpack.packb(result), copy=False)


def run_worker(port):
    message_handler(port)
