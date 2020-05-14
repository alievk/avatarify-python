import zmq
import numpy as np
import msgpack
import msgpack_numpy as m
m.patch()

from afy.utils import log


def check_connection(socket, timeout=1000):
    old_rcvtimeo = socket.RCVTIMEO
    socket.RCVTIMEO = timeout

    try:
        data = msgpack.packb(([], {}))
        socket.send_data('hello', data)
        attr_recv, data_recv = socket.recv_data()
        response = msgpack.unpackb(data_recv)
    except zmq.error.Again:
        return False
    finally:
        socket.RCVTIMEO = old_rcvtimeo

    log(f"Response to hello is {response}")
  
    return response == 'OK'


class SerializingSocket(zmq.Socket):
    """Numpy array serialization methods.

    Based on https://github.com/jeffbass/imagezmq/blob/master/imagezmq/imagezmq.py#L291

    Used for sending / receiving OpenCV images, which are Numpy arrays.
    Also used for sending / receiving jpg compressed OpenCV images.
    """

    def send_array(self, A, msg='NoName', flags=0, copy=True, track=False):
        """Sends a numpy array with metadata and text message.

        Sends a numpy array with the metadata necessary for reconstructing
        the array (dtype,shape). Also sends a text msg, often the array or
        image name.

        Arguments:
          A: numpy array or OpenCV image.
          msg: (optional) array name, image name or text message.
          flags: (optional) zmq flags.
          copy: (optional) zmq copy flag.
          track: (optional) zmq track flag.
        """

        md = dict(
            msg=msg,
            dtype=str(A.dtype),
            shape=A.shape,
        )
        self.send_json(md, flags | zmq.SNDMORE)
        return self.send(A, flags, copy=copy, track=track)

    def send_data(self,
                 msg='NoName',
                 data=b'00',
                 flags=0,
                 copy=True,
                 track=False):
        """Send a jpg buffer with a text message.

        Sends a jpg bytestring of an OpenCV image.
        Also sends text msg, often the image name.

        Arguments:
          msg: image name or text message.
          data: binary data to be sent.
          flags: (optional) zmq flags.
          copy: (optional) zmq copy flag.
          track: (optional) zmq track flag.
        """

        md = dict(msg=msg, )
        self.send_json(md, flags | zmq.SNDMORE)
        return self.send(data, flags, copy=copy, track=track)

    def recv_array(self, flags=0, copy=True, track=False):
        """Receives a numpy array with metadata and text message.

        Receives a numpy array with the metadata necessary
        for reconstructing the array (dtype,shape).
        Returns the array and a text msg, often the array or image name.

        Arguments:
          flags: (optional) zmq flags.
          copy: (optional) zmq copy flag.
          track: (optional) zmq track flag.

        Returns:
          msg: image name or text message.
          A: numpy array or OpenCV image reconstructed with dtype and shape.
        """

        md = self.recv_json(flags=flags)
        msg = self.recv(flags=flags, copy=copy, track=track)
        A = np.frombuffer(msg, dtype=md['dtype'])
        return (md['msg'], A.reshape(md['shape']))

    def recv_data(self, flags=0, copy=True, track=False):
        """Receives a jpg buffer and a text msg.

        Receives a jpg bytestring of an OpenCV image.
        Also receives a text msg, often the image name.

        Arguments:
          flags: (optional) zmq flags.
          copy: (optional) zmq copy flag.
          track: (optional) zmq track flag.

        Returns:
          msg: image name or text message.
          data: bytestring, containing data.
        """

        md = self.recv_json(flags=flags)  # metadata text
        data = self.recv(flags=flags, copy=copy, track=track)
        return (md['msg'], data)


class SerializingContext(zmq.Context):
    _socket_class = SerializingSocket
