from arguments import opt
from networking import SerializingContext, check_connection
from utils import log, TicToc, AccumDict, Once

import multiprocessing as mp
import queue

import cv2
import numpy as np
import zmq
import msgpack
import msgpack_numpy as m
m.patch()


PUT_TIMEOUT = 1 # s
GET_TIMEOUT = 1 # s
RECV_TIMEOUT = 1000 # ms
QUEUE_SIZE = 100


class PredictorRemote:
    def __init__(self, *args, remote_host=None, in_port=None, out_port=None, **kwargs):
        self.remote_host = remote_host
        self.in_port = in_port
        self.out_port = out_port
        self.predictor_args = (args, kwargs)
        self.timing = AccumDict()

        self.send_queue = mp.Queue(QUEUE_SIZE)
        self.recv_queue = mp.Queue(QUEUE_SIZE)

        self.worker_alive = mp.Value('i', 0)

        # if not self.remote_host.startswith("tcp://"):
        #     self.remote_host = "tcp://" + self.remote_host

        self.send_process = mp.Process(
            target=self.send_worker, 
            args=(self.remote_host, self.in_port, self.send_queue, self.worker_alive)
            )
        self.recv_process = mp.Process(
            target=self.recv_worker, 
            args=(self.remote_host, self.out_port, self.recv_queue, self.worker_alive)
            )

        # log("Connecting to remote host {self.remote_host}")
        # self.ctx = SerializingContext()
        # self.sender = self.ctx.socket(zmq.PUSH)
        # self.sender.connect(f"tcp://{remote_host}:5557")
        # self.receiver = self.ctx.socket(zmq.PULL)
        # self.receiver.connect(f"tcp://{remote_host}:5558")

        # if self.bind_port is None:
        #     if not self.remote_host.startswith("tcp://"):
        #         self.remote_host = "tcp://" + self.remote_host
        #     log(f"Connecting to {self.remote_host}")
        #     self.socket.connect(self.remote_host)

        #     if not check_connection(self.socket):
        #         self.socket.disconnect(self.remote_host)
        #         raise ConnectionError(f"Could not connect to {self.remote_host}")

        #     log(f"Connected to {self.remote_host}")
        # else:
        #     self.socket.bind(f"tcp://*:{self.bind_port}")
        #     log(f"Listening on port {self.bind_port}")

        #     # send OK to "hello" request from the peer 
        #     ok_msg = msgpack.packb("OK")
        #     self.socket.send_data("hello", ok_msg)

    def start(self):
        self.worker_alive.value = 1
        self.send_process.start()
        self.recv_process.start()

        self.init_remote_worker()

    def stop(self):
        self.worker_alive.value = 0
        log("join worker processes...")
        self.send_process.join(timeout=5)
        self.recv_process.join(timeout=5)

    def init_remote_worker(self):
        return self._send_recv_async('__init__', self.predictor_args, critical=True)

    def __getattr__(self, attr):
        is_critical = attr != 'predict'
        return lambda *args, **kwargs: self._send_recv_async(attr, (args, kwargs), critical=is_critical)

    # def _remote_call(self, method, args, critical=True):
        # if critical:
        #     return self._send_recv_sync(method, args)
        
        # return self._send_recv_async(method, args)

    # def _send_recv_sync(self, msg):
    #     method = msg['method']
    #     data = msgpack.packb(msg['args'])
    #     log('send', method)
    #     self.sender.send_data(method, data)

    #     while True:
    #         log('recv', method)
    #         method_recv, data_recv = self.receiver.recv_data()
    #         log('recved', method_recv)
    #         if method_recv == method:
    #             break

    #     return msgpack.unpackb(data_recv)

    def _send_recv_async(self, method, args, critical):
        args, kwargs = args

        tt = TicToc()
        tt.tic()
        if method == 'predict':
            image = args[0]
            assert isinstance(image, np.ndarray), 'Expected image'
            ret_code, data = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), opt.jpg_quality])
        else:
            data = msgpack.packb((args, kwargs))
        self.timing.add('PACK', tt.toc())

        meta = {
            'name': method,
            'critical': critical
        }

        # tt.tic()
        # self.socket.send_data(attr, data)
        # self.timing.add('SEND', tt.toc())
        if critical:
            log('send', meta)
            self.send_queue.put((meta, data))

            while True:
                log('recv', meta)
                meta_recv, data_recv = self.recv_queue.get()
                log('recved', meta_recv)
                if meta_recv == meta:
                    break
        else:
            try:
                # TODO: find good timeout
                self.send_queue.put((meta, data), timeout=PUT_TIMEOUT)
            except queue.Full:
                log('send_queue is full')

            # tt.tic()
            # attr_recv, data_recv = self.socket.recv_data()
            # self.timing.add('RECV', tt.toc())
            try:
                meta_recv, data_recv = self.recv_queue.get(timeout=0.01)
            except queue.Empty:
                log('recv_queue is empty')
                return None

        tt.tic()
        if meta_recv['name'] == 'predict':
            result = cv2.imdecode(np.frombuffer(data_recv, dtype='uint8'), -1)
        else:
            result = msgpack.unpackb(data_recv)
        self.timing.add('UNPACK', tt.toc())

        Once(self.timing, per=1)

        return result

    @staticmethod
    def send_worker(host, port, send_queue, worker_alive):
        address = f"tcp://{host}:{port}"

        ctx = SerializingContext()
        sender = ctx.socket(zmq.PUSH)
        sender.connect(address)

        log(f"Sending to {address}")

        try:
            while worker_alive.value:
                try:
                    msg = send_queue.get(timeout=GET_TIMEOUT)
                except queue.Empty:
                    continue

                sender.send_data(*msg)
        except KeyboardInterrupt:
            log("send_worker: user interrupt")
        finally:
            worker_alive.value = 0

        sender.disconnect(address)
        log("send_worker exit")

    @staticmethod
    def recv_worker(host, port, recv_queue, worker_alive):
        address = f"tcp://{host}:{port}"

        ctx = SerializingContext()
        receiver = ctx.socket(zmq.PULL)
        receiver.connect(address)
        receiver.RCVTIMEO = RECV_TIMEOUT

        log(f"Receiving from {address}")

        try:
            while worker_alive.value:
                try:
                    msg = receiver.recv_data()
                except zmq.error.Again:
                    continue
                
                try:
                    recv_queue.put(msg, timeout=PUT_TIMEOUT)
                except queue.Full:
                    continue
        except KeyboardInterrupt:
            log("recv_worker: user interrupt")
        finally:
            worker_alive.value = 0

        receiver.disconnect(address)
        log("recv_worker exit")
