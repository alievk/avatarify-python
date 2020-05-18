#from predictor_local import PredictorLocal
from arguments import opt
from networking import SerializingContext, check_connection
from utils import log, TicToc, AccumDict, Once

import cv2
import numpy as np
import zmq
import msgpack
import msgpack_numpy as m
m.patch()

import queue
import multiprocessing as mp


PUT_TIMEOUT = 1
GET_TIMEOUT = 1
QUEUE_SIZE = 100


class PredictorLocal():
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, attr):
        return None


class PredictorWorker():
    def __init__(self, port_recv=5557, port_send=5558):
        self.recv_queue = mp.Queue(QUEUE_SIZE)
        self.send_queue = mp.Queue(QUEUE_SIZE)

        self.recv_process = mp.Process(target=self.recv_worker, args=(port_recv, self.recv_queue))
        self.predictor_process = mp.Process(target=self.predictor_worker, args=(self.recv_queue, self.send_queue))
        self.send_process = mp.Process(target=self.send_worker, args=(port_send, self.send_queue))
    
    def run(self):
        self.recv_process.start()
        self.predictor_process.start()
        self.send_process.start()

        self.recv_process.join()
        self.predictor_process.join()
        self.send_process.join()

    @staticmethod
    def recv_worker(port, recv_queue):
        timing = AccumDict()

        ctx = SerializingContext()
        socket = ctx.socket(zmq.PULL)
        socket.bind(f"tcp://*:{port}")

        log(f'Receiving on port {port}')

        while True:
            tt = TicToc()

            tt.tic()
            msg = socket.recv_data()
            timing.add('RECV', tt.toc())

            try:
                recv_queue.put(msg, timeout=PUT_TIMEOUT)
            except queue.Full:
                recv_queue.get()

            Once(timing, per=1)

    @staticmethod
    def predictor_worker(recv_queue, send_queue):
        predictor = None
        predictor_args = ()
        timing = AccumDict()
        
        while True:
            try:
                msg = recv_queue.get(timeout=GET_TIMEOUT)
            except queue.Empty:
                continue

            # get the latest msg from the queue
            while not recv_queue.empty():
                msg = recv_queue.get()
                print('skip')

            attr, data = msg

            try:
                tt.tic()
                if attr == 'predict':
                    image = cv2.imdecode(np.frombuffer(data, dtype='uint8'), -1)
                else:
                    args = msgpack.unpackb(data)
                timing.add('UNPACK', tt.toc())
            except ValueError:
                log("Invalid Message")
                continue

            tt.tic()
            if attr == "hello":
                result = "OK"
            elif attr == "__init__":
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
                ret_code, data_send = cv2.imencode(".jpg", result, [int(cv2.IMWRITE_JPEG_QUALITY), opt.jpg_quality])
            else:
                data_send = msgpack.packb(result)
            timing.add('PACK', tt.toc())

            try:
                send_queue.put((attr, data_send), timeout=PUT_TIMEOUT)
            except queue.Full:
                send_queue.get()

            Once(timing, per=1)

    @staticmethod
    def send_worker(port, send_queue):
        timing = AccumDict()

        ctx = SerializingContext()
        socket = ctx.socket(zmq.PUSH)
        socket.bind(f"tcp://*:{port}")

        log(f'Sending on port {port}')

        while True:
            try:
                msg = send_queue.get(timeout=GET_TIMEOUT)
            except queue.Empty:
                continue

            attr, data = msg

            tt.tic()
            socket.send_data(attr, data)
            timing.add('SEND', tt.toc())

            Once(timing, per=1)


# def message_handler(bind_port=None, connect_address=None):
#     log("Creating socket")
#     context = SerializingContext()
#     socket = context.socket(zmq.PAIR)

#     if bind_port is None:
#         if not connect_address.startswith("tcp://"):
#             connect_address = "tcp://" + connect_address
#         log(f"Connecting to {connect_address}")
#         socket.connect(connect_address)

#         if not check_connection(socket):
#             socket.disconnect(connect_address)
#             raise ConnectionError(f"Could not connect to {connect_address}")

#         log(f"Connected to {connect_address}")
#     else:
#         socket.bind(f"tcp://*:{bind_port}")
#         log(f"Listening for messages on port {bind_port}")

#     predictor = None
#     predictor_args = ()
#     timing = AccumDict()
    
#     try:
#         while True:
#             tt = TicToc()

#             tt.tic()
#             attr, data = socket.recv_data()
#             timing.add('RECV', tt.toc())

#             try:
#                 tt.tic()
#                 if attr == 'predict':
#                     image = cv2.imdecode(np.frombuffer(data, dtype='uint8'), -1)
#                 else:
#                     args = msgpack.unpackb(data)
#                 timing.add('UNPACK', tt.toc())
#             except ValueError:
#                 log("Invalid Message")
#                 continue

#             tt.tic()
#             if attr == "hello":
#                 result = "OK"
#             elif attr == "__init__":
#                 if args == predictor_args:
#                     log("Same config as before... reusing previous predictor")
#                 else:
#                     del predictor
#                     predictor_args = args
#                     predictor = PredictorLocal(*predictor_args[0], **predictor_args[1])
#                     log("Initialized predictor with:", predictor_args)
#                 result = True
#                 tt.tic() # don't account for init
#             elif attr == 'predict':
#                 result = getattr(predictor, attr)(image)
#             else:
#                 result = getattr(predictor, attr)(*args[0], **args[1])
#             timing.add('CALL', tt.toc())

#             tt.tic()
#             if attr == 'predict':
#                 assert isinstance(result, np.ndarray), 'Expected image'
#                 ret_code, data_send = cv2.imencode(".jpg", result, [int(cv2.IMWRITE_JPEG_QUALITY), opt.jpg_quality])
#             else:
#                 data_send = msgpack.packb(result)
#             timing.add('PACK', tt.toc())

#             tt.tic()
#             socket.send_data(attr, data_send)
#             timing.add('SEND', tt.toc())

#             Once(timing, per=1)
#     except KeyboardInterrupt:
#         pass

def run_worker(bind_port=None, connect_address=None):
    worker = PredictorWorker()
    worker.run()
