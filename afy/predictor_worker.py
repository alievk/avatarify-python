from predictor_local import PredictorLocal
from arguments import opt
from networking import SerializingContext, check_connection
from utils import Logger, TicToc, AccumDict, Once

import cv2
import numpy as np
import zmq
import msgpack
import msgpack_numpy as m
m.patch()

import queue
import multiprocessing as mp
import traceback
import time


PUT_TIMEOUT = 1 # s
GET_TIMEOUT = 1 # s
RECV_TIMEOUT = 1000 # ms
QUEUE_SIZE = 100


# class PredictorLocal():
#     def __init__(self, *args, **kwargs):
#         pass

#     def __getattr__(self, *args, **kwargs):
#         return lambda *args, **kwargs: None


class PredictorWorker():
    def __init__(self, in_port=None, out_port=None):
        self.recv_queue = mp.Queue(QUEUE_SIZE)
        self.send_queue = mp.Queue(QUEUE_SIZE)

        self.worker_alive = mp.Value('i', 0)

        self.recv_process = mp.Process(target=self.recv_worker, args=(in_port, self.recv_queue, self.worker_alive))
        self.predictor_process = mp.Process(target=self.predictor_worker, args=(self.recv_queue, self.send_queue, self.worker_alive))
        self.send_process = mp.Process(target=self.send_worker, args=(out_port, self.send_queue, self.worker_alive))
    
    def run(self):
        self.worker_alive.value = 1

        self.recv_process.start()
        self.predictor_process.start()
        self.send_process.start()

        try:
            self.recv_process.join()
            self.predictor_process.join()
            self.send_process.join()
        except KeyboardInterrupt:
            pass

    @staticmethod
    def recv_worker(port, recv_queue, worker_alive):
        timing = AccumDict()
        log = Logger('./var/log/recv_worker.log', verbose=opt.verbose)

        ctx = SerializingContext()
        socket = ctx.socket(zmq.PULL)
        socket.bind(f"tcp://*:{port}")
        socket.RCVTIMEO = RECV_TIMEOUT

        log(f'Receiving on port {port}', important=True)

        try:
            while worker_alive.value:
                tt = TicToc()

                try:
                    tt.tic()
                    msg = socket.recv_data()
                    timing.add('RECV', tt.toc())
                except zmq.error.Again:
                    log("recv timeout")
                    continue

                #log('recv', msg[0])

                method, data = msg
                if method['critical']:
                    recv_queue.put(msg)
                else:
                    try:
                        recv_queue.put(msg, block=False)
                    except queue.Full:
                        log('recv_queue full')

                Once(timing, log, per=1)
        except KeyboardInterrupt:
            log("recv_worker: user interrupt", important=True)

        worker_alive.value = 0
        log("recv_worker exit", important=True)

    @staticmethod
    def predictor_worker(recv_queue, send_queue, worker_alive):
        predictor = None
        predictor_args = ()
        timing = AccumDict()
        log = Logger('./var/log/predictor_worker.log', verbose=opt.verbose)
        
        try:
            while worker_alive.value:
                tt = TicToc()

                try:
                    method, data = recv_queue.get(timeout=GET_TIMEOUT)
                except queue.Empty:
                    continue

                # get the latest non-critical request from the queue
                # don't skip critical request
                while not recv_queue.empty() and not method['critical']:
                    log(f"skip {method}")
                    method, data = recv_queue.get()

                log("working on", method)

                try:
                    tt.tic()
                    if method['name'] == 'predict':
                        image = cv2.imdecode(np.frombuffer(data, dtype='uint8'), -1)
                    else:
                        args = msgpack.unpackb(data)
                    timing.add('UNPACK', tt.toc())
                except ValueError:
                    log("Invalid Message", important=True)
                    continue

                tt.tic()
                if method['name'] == "hello":
                    result = "OK"
                elif method['name'] == "__init__":
                    if args == predictor_args:
                        log("Same config as before... reusing previous predictor")
                    else:
                        del predictor
                        predictor_args = args
                        predictor = PredictorLocal(*predictor_args[0], **predictor_args[1])
                        log("Initialized predictor with:", predictor_args, important=True)
                    result = True
                    tt.tic() # don't account for init
                elif method['name'] == 'predict':
                    assert predictor is not None, "Predictor was not initialized"
                    result = getattr(predictor, method['name'])(image)
                else:
                    assert predictor is not None, "Predictor was not initialized"
                    result = getattr(predictor, method['name'])(*args[0], **args[1])
                timing.add('CALL', tt.toc())

                tt.tic()
                if method['name'] == 'predict':
                    assert isinstance(result, np.ndarray), f'Expected np.ndarray, got {result.__class__}'
                    ret_code, data_send = cv2.imencode(".jpg", result, [int(cv2.IMWRITE_JPEG_QUALITY), opt.jpg_quality])
                else:
                    data_send = msgpack.packb(result)
                timing.add('PACK', tt.toc())

                if method['critical']:
                    send_queue.put((method, data_send))
                else:
                    try:
                        send_queue.put((method, data_send), block=False)
                    except queue.Full:
                        log("send_queue full")
                        pass

                Once(timing, log, per=1)
        except KeyboardInterrupt:
            log("predictor_worker: user interrupt", important=True)
        except Exception as e:
            log("predictor_worker error", important=True)
            traceback.print_exc()
    
        worker_alive.value = 0
        log("predictor_worker exit", important=True)

    @staticmethod
    def send_worker(port, send_queue, worker_alive):
        timing = AccumDict()
        log = Logger('./var/log/send_worker.log', verbose=opt.verbose)

        ctx = SerializingContext()
        socket = ctx.socket(zmq.PUSH)
        socket.bind(f"tcp://*:{port}")

        log(f'Sending on port {port}', important=True)

        try:
            while worker_alive.value:
                tt = TicToc()

                try:
                    method, data = send_queue.get(timeout=GET_TIMEOUT)
                except queue.Empty:
                    log("send queue empty")
                    continue

                # get the latest non-critical request from the queue
                # don't skip critical request
                while not send_queue.empty() and not method['critical']:
                    log(f"skip {method}")
                    method, data = send_queue.get()

                log("sending", method)

                tt.tic()
                socket.send_data(method, data)
                timing.add('SEND', tt.toc())

                Once(timing, log, per=1)
        except KeyboardInterrupt:
            log("predictor_worker: user interrupt", important=True)

        worker_alive.value = 0
        log("send_worker exit", important=True)


def run_worker(in_port=None, out_port=None):
    worker = PredictorWorker(in_port=in_port, out_port=out_port)
    worker.run()
