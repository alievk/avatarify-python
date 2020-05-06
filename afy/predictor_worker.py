from predictor_local import PredictorLocal
from arguments import opt
from networking import SerializingContext
from utils import log, TicToc, AccumDict, Once

import cv2
import numpy as np
import zmq
import msgpack
import msgpack_numpy as m
m.patch()


def message_handler(port):
    log("Creating socket")
    context = SerializingContext()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % port)
    log("Listening for messages on port:", port)

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
            if attr == "__init__":
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

def run_worker(port):
    message_handler(port)
