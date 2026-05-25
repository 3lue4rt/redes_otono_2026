import socket
from random import randint

DEBUG_FLAG = False

def debug(msg: object):
    print(msg) if DEBUG_FLAG else None

class SocketTCP:
    def __init__(self):
        debug("Creando socket UDP")
        self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.direccion_destino: tuple[str, int] | None  = None
        self.direccion_origen: tuple[str, int] | None = None
        self.seq: int | None = None

    @staticmethod
    def debug(msg: object):
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
        debug("Parseando segmento")
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
        debug("Creando segmento")
        byte1 = segment.SYN*(2**7) + segment.ACK*(2**6) + segment.FIN*(2**5) + (segment.seq >> 8)
        debug(f"primer byte: {format(byte1, 'b')}")
        byte2 = segment.seq & (2**8 - 1)
        debug(f"segundo byte: {format(byte2, 'b')}")
        debug(f"resto de la data: {segment.data}")
        debug(f"SYN: {segment.SYN}")
        debug(f"ACK: {segment.ACK}")
        debug(f"FIN: {segment.FIN}")
        debug(f"n° de secuencia: {segment.seq} (en binario: {format(segment.seq, 'b')})")
        return bytes([byte1, byte2]) + segment.data

    def bind(self, address: tuple[str, int]):
        "El socket escucha en la dirección address"
        self.direccion_origen = address
        debug(f"El socket queda bindeado a la dirección {address}")
        self.socket_udp.bind(address)

    def connect(self, address: tuple[str, int]):
        "El SocketTCP se conecta con otro SocketTCP en la dirección address usando el 3-way handshake"
        self.seq = randint(0, 100)
        #primer handshake
        debug("Creando el primer handshake")
        handshake_1 = self.create_segment(Segment(SYN=True, 
                                                  ACK=False, 
                                                  FIN=False, 
                                                  seq=self.seq, 
                                                  data=bytes()))
        debug("Mandando el primer hanshake")
        self.socket_udp.sendto(handshake_1, address)
        #segundo handshake
        debug("Recibiendo el segundo handshake")
        handshake_2, incoming_address = self.socket_udp.recvfrom(2)
        parsed_shake = self.parse_segment(handshake_2)
        """ if not (parsed_shake.SYN and parsed_shake.ACK and self.seq + 1 == parsed_shake.seq):
            raise Exception("El SocketTCP no pudo completar el 3-way handshake (handshake 2)") """
        self.seq = parsed_shake.seq + 1
        #tercer handshake
        debug("Creando el tercer handshake")
        handshake_3 = self.create_segment(Segment(SYN=False, 
                                                  ACK=True, 
                                                  FIN=False, 
                                                  seq=self.seq, 
                                                  data=bytes()))
        debug("Mandando el tercer handshake")
        self.socket_udp.sendto(handshake_3, address)
        #si todo está en orden podemos guardar la dirección del SocketTCP servidor para futuro uso
        debug(f"Ahora me comunico con {incoming_address}")
        self.direccion_destino = incoming_address

    def accept(self) -> tuple[SocketTCP, tuple[str, int]]:
        "El socketTCP acepta la conección de un SocketTCP 's', retornando otro SocketTCP y la dirección de s"
        #esperamos el primer handshake
        debug("Recibiendo el primer handshake")
        handshake_1, incoming_address = self.socket_udp.recvfrom(2)
        parsed_shake = self.parse_segment(handshake_1)
        """ if not parsed_shake.SYN or parsed_shake.ACK or parsed_shake.FIN:
            raise Exception("El SocketTCP no pudo completar el 3-way handshake (handshake 1)") """
        self.seq = parsed_shake.seq + 1
        #mandamos el segundo handshake con el nuevo socket
        debug("Creando el segundo handshake")
        handshake_2 = self.create_segment(Segment(SYN=True, 
                                                  ACK=True, 
                                                  FIN=False, 
                                                  seq=self.seq, 
                                                  data=bytes()))
        #nuevo socket para la comunicación
        new_sock = SocketTCP()
        debug("Enviando el segundo handshake con el nuevo socket")
        new_sock.socket_udp.sendto(handshake_2, incoming_address)
        #esperamos el tercer handshake
        debug("Recibiendo el tercer handshake")
        handshake_3, incoming_address = self.socket_udp.recvfrom(2)
        parsed_shake = self.parse_segment(handshake_3)
        """ if not parsed_shake.SYN or parsed_shake.ACK or parsed_shake.FIN:
            raise Exception("El SocketTCP no pudo completar el 3-way handshake (handshake 3)") """
        #el nuevo socket estará encargado de la comunicación
        #con el cliente de ahora en adelante, lo dejamos seteado
        new_sock.direccion_destino = incoming_address
        new_sock.direccion_origen = new_sock.socket_udp.getsockname()
        return new_sock, incoming_address


    

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
    
    def __str__(self):
        "Printeamos los atributos del header para mejor debugueo"
        return str(vars(self))