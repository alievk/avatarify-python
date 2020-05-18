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
    def __init__(self, *args, bind_port=None, connect_address=None, **kwargs):
        self.bind_port = bind_port
        self.connect_address = connect_address
        self.predictor_args = (args, kwargs)
        self.timing = AccumDict()

        self.send_queue = mp.Queue(QUEUE_SIZE)
        self.recv_queue = mp.Queue(QUEUE_SIZE)

        self.worker_alive = mp.Value('i', 0)

        # if not self.connect_address.startswith("tcp://"):
        #     self.connect_address = "tcp://" + self.connect_address

        self.send_process = mp.Process(target=self.send_worker, args=(self.connect_address, self.send_queue, self.worker_alive))
        self.recv_process = mp.Process(target=self.recv_worker, args=(self.connect_address, self.recv_queue, self.worker_alive))

        # self.context = SerializingContext()
        # self.socket = self.context.socket(zmq.PAIR)

        # if self.bind_port is None:
        #     if not self.connect_address.startswith("tcp://"):
        #         self.connect_address = "tcp://" + self.connect_address
        #     log(f"Connecting to {self.connect_address}")
        #     self.socket.connect(self.connect_address)

        #     if not check_connection(self.socket):
        #         self.socket.disconnect(self.connect_address)
        #         raise ConnectionError(f"Could not connect to {self.connect_address}")

        #     log(f"Connected to {self.connect_address}")
        # else:
        #     self.socket.bind(f"tcp://*:{self.bind_port}")
        #     log(f"Listening on port {self.bind_port}")

        #     # send OK to "hello" request from the peer 
        #     ok_msg = msgpack.packb("OK")
        #     self.socket.send_data("hello", ok_msg)

        self.init_remote_worker()

    def start(self):
        self.worker_alive.value = 1
        self.send_process.start()
        self.recv_process.start()

    def stop(self):
        self.worker_alive.value = 0
        log("join worker processes...")
        self.send_process.join(timeout=5)
        self.recv_process.join(timeout=5)

    def init_remote_worker(self):
        return self._remote_call('__init__', self.predictor_args, critical=True)

    def __getattr__(self, attr):
        is_critical = attr != 'predict'
        return lambda *args, **kwargs: self._remote_call(attr, (args, kwargs), critical=is_critical)

    def _remote_call(self, method, args, critical=True):
        msg = {
            'method': {
                'name': attr,
                'critical': critical
            },
            'args': args
        }

        if critical:
            return self._send_recv_sync(msg)
        
        return self._send_recv_async(msg)

    def _send_recv_sync(self, msg):
        method = msg['method']
        data = msgpack.packb(msg['args'])
        self.socket.send_data(method, data)

        while True:
            method_recv, data_recv = self.socket.recv_data()
            if method_recv == method:
                break

        return msgpack.unpackb(data_recv)

    def _send_recv_async(self, msg):
        method = msg['method']
        args, kwargs = msg['args']

        tt = TicToc()
        tt.tic()
        if method['name'] == 'predict':
            image = args[0]
            assert isinstance(image, np.ndarray), 'Expected image'
            ret_code, data = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), opt.jpg_quality])
        else:
            data = msgpack.packb((args, kwargs))
        self.timing.add('PACK', tt.toc())

        # tt.tic()
        # self.socket.send_data(attr, data)
        # self.timing.add('SEND', tt.toc())
        try:
            self.send_queue.put((method, data), timeout=PUT_TIMEOUT)
        except queue.Full:
            log('send_queue is full')

        # tt.tic()
        # attr_recv, data_recv = self.socket.recv_data()
        # self.timing.add('RECV', tt.toc())
        try:
            method_recv, data_recv = self.recv_queue.get(timeout=0.01)
        except queue.Empty:
            log('recv_queue is empty')
            return None

        tt.tic()
        if method_recv['name'] == 'predict':
            result = cv2.imdecode(np.frombuffer(data_recv, dtype='uint8'), -1)
        else:
            result = msgpack.unpackb(data_recv)
        self.timing.add('UNPACK', tt.toc())

        Once(self.timing, per=1)

        return result

    @staticmethod
    def send_worker(host, send_queue, worker_alive):
        address = f"tcp://{host}:5557"

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
    def recv_worker(host, recv_queue, worker_alive):
        address = f"tcp://{host}:5558"

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
