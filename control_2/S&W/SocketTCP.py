import socket

DEBUG_FLAG = False

def debug(msg: object):
    print(msg) if DEBUG_FLAG else None

class SocketTCP:
    def __init__(self):
        debug("Creando socket UDP")
        self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.direccion_destino = None
        self.direccion_origen = self.socket_udp.getsockname()

    def debug(self, msg: object):
        print(msg) if DEBUG_FLAG else None

    @staticmethod
    def parse_segment(segment: bytes) -> Segment:
        "Toma un segmento de 2+n bytes y lo transforma en una instancia de Segment"
        """Formato del segmento:
         0                   1
         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |S|A|F|                         |
        |Y|C|I|           seq           |
        |N|K|N|                         |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                               |
        /             data              /
        /                               /
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        """
        debug(f"Parseando segmento {segment}")
        byte1 = segment[0]
        debug(f"primer byte: {format(byte1, 'b')}")
        byte2 = segment[1]
        debug(f"segundo byte: {format(byte2, 'b')}")
        data = segment[2:]
        debug(f"resto de la data: {data}")
        SYN = bool(byte1 >> 7)
        debug(f"SYN: {SYN}")
        ACK = bool((byte1 >> 6) & 1)
        debug(f"ACK: {ACK}")
        FIN = bool((byte1 >> 5) & 1)
        debug(f"FIN: {FIN}")
        seq = ((byte1 & (2**5 -1)) << 8) + byte2
        debug(f"n° de secuencia: {seq} (en binario: {format(seq, 'b')})")
        return Segment(SYN, ACK, FIN, seq, data)
    
    @staticmethod
    def create_segment(segment: Segment) -> bytes:
        "Toma una instancia de Segment y devuelve un segmento de 2+n bytes"
        debug(f"Creando segmento a partir del segmento: {segment}")
        byte1 = segment.SYN*(2**7) + segment.ACK*(2**6) + segment.FIN*(2**5) + (segment.seq >> 8)
        debug(f"primer byte: {format(byte1, 'b')}")
        byte2 = segment.seq & (2**8 - 1)
        debug(f"segundo byte: {format(byte2, 'b')}")
        return bytes([byte1, byte2]) + segment.data


class Segment:
    """Representa un segmento de 2+n bytes, los 2 primeros bytes son el header, 
    solo tiene flags para SYN, ACK y FIN, más 13 bits para un n° de seq,
    los n bytes restantes son datos"""
    def __init__(self, SYN: bool, ACK: bool, FIN: bool, seq: int, data: bytes):
        self.SYN = SYN
        self.ACK = ACK
        self.FIN = FIN
        self.seq = seq%(2**13)
        self.data = data
        debug(f"Creando el segmento: {self}")
    
    def __str__(self):
        "Printeamos los atributos del header para mejor debugueo"
        return str(vars(self))