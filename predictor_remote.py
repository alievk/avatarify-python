from predictor_local import PredictorLocal
from arguments import opt

import zmq
import msgpack
import msgpack_numpy as m
m.patch()


DEFAULT_PORT = 5556


class PredictorRemote:
    def __init__(self, worker_host='localhost', worker_port=DEFAULT_PORT, **kwargs):
        self.worker_host = worker_host
        self.worker_port = worker_port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.connect(f"tcp://{worker_host}:{worker_port}")
        print(f"Connected to {worker_host}:{worker_port}")
        self.predictor_args = kwargs
        self.init_worker()

    def init_worker(self):
        msg = (
            2,
            self.predictor_args,
        )
        return self._send_recv_msg(msg)

    def _send_recv_msg(self, msg):
        self.socket.send(msgpack.packb(msg), copy=False)
        response = self.socket.recv()
        return msgpack.unpackb(response)

    def predict(self, driving_frame, source_image):
        msg = (
            0,
            driving_frame,
            source_image,
        )
        return self._send_recv_msg(msg)

    def get_frame_kp(self, image):
        msg = (
            1,
            image,
        )
        return self._send_recv_msg(msg)


def message_handler(port):
    print("Creating socket")
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % port)
    predictor = None
    predictor_args = {}

    print("Listening for messages on port:", port)
    while True:
        msg_raw = socket.recv()
        print("Got message")
        try:
            msg = msgpack.unpackb(msg_raw)
        except ValueError:
            print("Invalid Message")
            continue
        method = msg[0]
        if method == 0:
            result = predictor.predict(*msg[1:])
        elif method == 1:
            result = predictor.get_frame_kp(*msg[1:])
        elif method == 2:
            predictor_args_new = msg[1]
            if predictor_args_new == predictor_args:
                print("Same config as before... reusing previous predictor")
            else:
                del predictor
                predictor_args = predictor_args_new
                predictor = PredictorLocal(**predictor_args)
                print("Initialized predictor with:", predictor_args)
            result = True
        print(f"Sending result of {method}")
        socket.send(msgpack.packb(result), copy=False)


def run_worker(port):
    message_handler(port)
