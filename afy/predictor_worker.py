from predictor_local import PredictorLocal
from arguments import opt
from networking import SerializingContext, check_connection
from utils import log, TicToc, AccumDict, Once

import cv2
import numpy as np
import zmq
import msgpack
import msgpack_numpy as m
m.patch()


def message_handler(bind_port=None, connect_address=None):
    log("Creating socket")
    context = SerializingContext()
    socket = context.socket(zmq.PAIR)

    if bind_port is None:
        if not connect_address.startswith("tcp://"):
            connect_address = "tcp://" + connect_address
        log(f"Connecting to {connect_address}")
        socket.connect(connect_address)

        if not check_connection(socket):
            self.socket.disconnect(connect_address)
            raise ConnectionError(f"Could not connect to {connect_address}")

        log(f"Connected to {connect_address}")
    else:
        socket.bind("tcp://*:%s" % bind_port)
        log("Listening for messages on port:", bind_port)

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

            tt.tic()
            socket.send_data(attr, data_send)
            timing.add('SEND', tt.toc())

            Once(timing, per=1)
    except KeyboardInterrupt:
        pass

def run_worker(bind_port=None, connect_address=None):
    message_handler(bind_port, connect_address)
