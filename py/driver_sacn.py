from bibliopixel.drivers.driver_base import DriverBase
from e131packet import E131Packet
import socket
import sys
import time
import struct

import os
os.sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bibliopixel.log as log


class CMDTYPE:
    SETUP_DATA = 1  # reserved for future use
    PIXEL_DATA = 2
    BRIGHTNESS = 3


class RETURN_CODES:
    SUCCESS = 255  # All is well
    ERROR = 0  # Generic error
    ERROR_SIZE = 1  # Data receieved does not match given command length
    ERROR_UNSUPPORTED = 2  # Unsupported command


class DriverSACN(DriverBase):
    """Driver for communicating with another device on the network."""

    def __init__(self, num=0, width=0, height=0, host="localhost", broadcast=False, port=5568, broadcast_interface=''):
        super(DriverSACN, self).__init__(num, width, height)

        self._host = host
        self._port = port
        self._sock = None
        self._broadcast = broadcast
        self._broadcast_interface = broadcast_interface


# s = socket(AF_INET, SOCK_DGRAM)
# s.bind(('', 0))
# s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    def _connect(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            if self._broadcast:
                # self._sock.bind((self._broadcast_interface, self._port))
                self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            ttl = struct.pack('b',1)
            self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

            self._sock.settimeout(0.2)

            return self._sock
        except socket.gaierror:
            error = "Unable to connect to or resolve host: {}".format(
                self._host)
            log.error(error)
            raise IOError(error)

    # Push new data to strand
    def update(self, data):
        try:
            self._fixData(data)
            data = self._buf
            s = self._connect()

            count = self.bufByteCount
            packet = E131Packet(universe=1, data=data)

            s.sendto(packet.packet_data, (self._host, self._port))

            s.close()

        except Exception as e:
            log.exception(e)
            error = "Problem communicating with network receiver!"
            log.error(error)
            raise IOError(error)


MANIFEST = [
    {
        "id": "network_udp",
        "class": DriverSACN,
        "type": "driver",
        "display": "sACN",
        "desc": "Sends pixel data over the network to a E1.31/sACN reciever.",
        "params": [{
                "id": "num",
                "label": "# Pixels",
                "type": "int",
                "default": 0,
                "min": 0,
                "help": "Total pixels in display. May use Width AND Height instead."
        }, {
            "id": "width",
            "label": "Width",
            "type": "int",
            "default": 0,
            "min": 0,
            "help": "Width of display. Set if using a matrix."
        }, {
            "id": "height",
            "label": "Height",
            "type": "int",
            "default": 0,
            "min": 0,
            "help": "Height of display. Set if using a matrix."
        }, {
            "id": "host",
            "label": "Host IP",
            "type": "str",
            "default": "localhost",
            "help": "Receiver host to connect to."
        }, {
            "id": "port",
            "label": "Port",
            "type": "int",
            "default": 5568,
            "help": "Port to connect to."
        }]
    }
]
