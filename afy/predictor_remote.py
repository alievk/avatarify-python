from arguments import opt
from networking import SerializingContext, check_connection
from utils import Logger, TicToc, AccumDict, Once

import multiprocessing as mp
import queue

import cv2
import numpy as np
import zmq
import msgpack
import msgpack_numpy as m
m.patch()


PUT_TIMEOUT = 0.1 # s
GET_TIMEOUT = 0.1 # s
RECV_TIMEOUT = 1000 # ms
QUEUE_SIZE = 100


class PredictorRemote:
    def __init__(self, *args, in_addr=None, out_addr=None, **kwargs):
        self.in_addr = in_addr
        self.out_addr = out_addr
        self.predictor_args = (args, kwargs)
        self.timing = AccumDict()
        self.log = Logger('./var/log/predictor_remote.log', verbose=opt.verbose)

        self.send_queue = mp.Queue(QUEUE_SIZE)
        self.recv_queue = mp.Queue(QUEUE_SIZE)

        self.worker_alive = mp.Value('i', 0)

        self.send_process = mp.Process(
            target=self.send_worker, 
            args=(self.in_addr, self.send_queue, self.worker_alive),
            name="send_process"
            )
        self.recv_process = mp.Process(
            target=self.recv_worker, 
            args=(self.out_addr, self.recv_queue, self.worker_alive),
            name="recv_process"
            )

        self._i_msg = -1

    def start(self):
        self.worker_alive.value = 1
        self.send_process.start()
        self.recv_process.start()

        self.init_remote_worker()

    def stop(self):
        self.worker_alive.value = 0
        self.log("join worker processes...")
        self.send_process.join(timeout=5)
        self.recv_process.join(timeout=5)
        self.send_process.terminate()
        self.recv_process.terminate()

    def init_remote_worker(self):
        return self._send_recv_async('__init__', self.predictor_args, critical=True)

    def __getattr__(self, attr):
        is_critical = attr != 'predict'
        return lambda *args, **kwargs: self._send_recv_async(attr, (args, kwargs), critical=is_critical)

    def _send_recv_async(self, method, args, critical):
        self._i_msg += 1

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
            'critical': critical,
            'id': self._i_msg
        }

        self.log("send", meta)

        if critical:
            self.send_queue.put((meta, data))

            while True:
                meta_recv, data_recv = self.recv_queue.get()
                if meta_recv == meta:
                    break
        else:
            try:
                # TODO: find good timeout
                self.send_queue.put((meta, data), timeout=PUT_TIMEOUT)
            except queue.Full:
                self.log('send_queue is full')

            try:
                meta_recv, data_recv = self.recv_queue.get(timeout=GET_TIMEOUT)
            except queue.Empty:
                self.log('recv_queue is empty')
                return None

        self.log("recv", meta_recv)

        tt.tic()
        if meta_recv['name'] == 'predict':
            result = cv2.imdecode(np.frombuffer(data_recv, dtype='uint8'), -1)
        else:
            result = msgpack.unpackb(data_recv)
        self.timing.add('UNPACK', tt.toc())

        if opt.verbose:
            Once(self.timing, per=1)

        return result

    @staticmethod
    def send_worker(address, send_queue, worker_alive):
        timing = AccumDict()
        log = Logger('./var/log/send_worker.log', opt.verbose)

        ctx = SerializingContext()
        sender = ctx.socket(zmq.PUSH)
        sender.connect(address)

        log(f"Sending to {address}")

        try:
            while worker_alive.value:
                tt = TicToc()

                try:
                    msg = send_queue.get(timeout=GET_TIMEOUT)
                except queue.Empty:
                    continue

                tt.tic()
                sender.send_data(*msg)
                timing.add('SEND', tt.toc())

                if opt.verbose:
                    Once(timing, log, per=1)
        except KeyboardInterrupt:
            log("send_worker: user interrupt")
        finally:
            worker_alive.value = 0

        sender.disconnect(address)
        sender.close()
        ctx.destroy()
        log("send_worker exit")

    @staticmethod
    def recv_worker(address, recv_queue, worker_alive):
        timing = AccumDict()
        log = Logger('./var/log/recv_worker.log')

        ctx = SerializingContext()
        receiver = ctx.socket(zmq.PULL)
        receiver.connect(address)
        receiver.RCVTIMEO = RECV_TIMEOUT

        log(f"Receiving from {address}")

        try:
            while worker_alive.value:
                tt = TicToc()

                try:
                    tt.tic()
                    msg = receiver.recv_data()
                    timing.add('RECV', tt.toc())
                except zmq.error.Again:
                    continue
                
                try:
                    recv_queue.put(msg, timeout=PUT_TIMEOUT)
                except queue.Full:
                    log('recv_queue full')
                    continue

                if opt.verbose:
                    Once(timing, log, per=1)
        except KeyboardInterrupt:
            log("recv_worker: user interrupt")
        finally:
            worker_alive.value = 0

        receiver.disconnect(address)
        receiver.close()
        ctx.destroy()
        log("recv_worker exit")
