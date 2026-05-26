import socket
from random import randint

DEBUG_FLAG = False
TCP_HEADER_SIZE = 2
PACKET_SIZE_MAX = 16 + TCP_HEADER_SIZE
TIMEOUT_TIME = 3

def debug(msg: object):
    print(msg) if DEBUG_FLAG else None

class SocketTCP:
    def __init__(self):
        debug("Creando socket UDP")
        self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.direccion_destino: tuple[str, int] | None  = None
        self.direccion_origen: tuple[str, int] | None = None
        self.seq: int | None = None
        self.bytes_left_to_read = 0

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
        #debug("Parseando segmento")
        byte1 = segment[0]
        #debug(f"primer byte: {format(byte1, 'b')}")
        byte2 = segment[1]
        #debug(f"segundo byte: {format(byte2, 'b')}")
        data = segment[2:]
        #debug(f"resto de la data: {data}")
        SYN = bool(byte1 >> 7)
        #debug(f"SYN: {SYN}")
        ACK = bool((byte1 >> 6) & 1)
        #debug(f"ACK: {ACK}")
        FIN = bool((byte1 >> 5) & 1)
        #debug(f"FIN: {FIN}")
        seq = ((byte1 & (2**5 -1)) << 8) + byte2
        #debug(f"n° de secuencia: {seq} (en binario: {format(seq, 'b')})")
        ret = Segment(SYN, ACK, FIN, seq, data)
        debug(ret)
        return ret
    
    @staticmethod
    def create_segment(segment: Segment) -> bytes:
        "Toma una instancia de Segment y devuelve un segmento de 2+n bytes"
        debug(f"Creando segmento {segment}")
        byte1 = segment.SYN*(2**7) + segment.ACK*(2**6) + segment.FIN*(2**5) + (segment.seq >> 8)
        #debug(f"primer byte: {format(byte1, 'b')}")
        byte2 = segment.seq & (2**8 - 1)
        #debug(f"segundo byte: {format(byte2, 'b')}")
        #debug(f"resto de la data: {segment.data}")
        #debug(f"SYN: {segment.SYN}")
        #debug(f"ACK: {segment.ACK}")
        #debug(f"FIN: {segment.FIN}")
        #debug(f"n° de secuencia: {segment.seq} (en binario: {format(segment.seq, 'b')})")
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
        handshake_2, incoming_address = self.socket_udp.recvfrom(TCP_HEADER_SIZE)
        parsed_shake = self.parse_segment(handshake_2)
        """ if not (parsed_shake.SYN and parsed_shake.ACK and self.seq + 1 == parsed_shake.seq):
            raise Exception("El SocketTCP no pudo completar el 3-way handshake (handshake 2)") """
        #este n° de secuencia será el utilizado por send()
        self.seq = parsed_shake.seq + 1
        #tercer handshake
        debug("Creando el tercer handshake")
        handshake_3 = self.create_segment(Segment(SYN=False, 
                                                  ACK=True, 
                                                  FIN=False, 
                                                  seq=self.seq, 
                                                  data=bytes()))
        debug("Mandando el tercer handshake")
        self.socket_udp.sendto(handshake_3, incoming_address)
        #si todo está en orden podemos guardar la dirección del SocketTCP servidor para futuro uso
        debug(f"Ahora me comunico con {incoming_address}")
        self.direccion_destino = incoming_address

    def accept(self) -> tuple[SocketTCP, tuple[str, int]]:
        "El socketTCP acepta la conección de un SocketTCP 's', retornando otro SocketTCP y la dirección de s"
        #esperamos el primer handshake
        debug("Recibiendo el primer handshake")
        handshake_1, incoming_address = self.socket_udp.recvfrom(TCP_HEADER_SIZE)
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
        handshake_3, incoming_address = new_sock.socket_udp.recvfrom(TCP_HEADER_SIZE)
        parsed_shake = self.parse_segment(handshake_3)
        """ if not parsed_shake.SYN or parsed_shake.ACK or parsed_shake.FIN:
            raise Exception("El SocketTCP no pudo completar el 3-way handshake (handshake 3)") """
        #el nuevo socket estará encargado de la comunicación
        #con el cliente de ahora en adelante, lo dejamos seteado
        new_sock.seq = parsed_shake.seq
        new_sock.direccion_destino = incoming_address
        new_sock.direccion_origen = new_sock.socket_udp.getsockname()
        return new_sock, incoming_address

    def send(self, message: bytes):
        if self.seq==None or self.direccion_destino==None:
            debug("El socket nunca se conectó a algún servidor, abortando send")
            return
        self.socket_udp.settimeout(TIMEOUT_TIME)
        debug(f"Enviando a {self.direccion_destino}\nTamaño máximo de paquete {PACKET_SIZE_MAX} bytes")
        message_length = len(message)
        debug(f"Leído el siguiente mensaje:\n{message}\n Largo: {message_length}")
        debug("Creando segmento 0 con el largo del mensaje")
        segmento_0 = self.create_segment(Segment(SYN=False,
                                                 ACK=False,
                                                 FIN=False,
                                                 seq=self.seq,
                                                 data=str(message_length).encode()))
        debug("Mandando segmento 0")
        self.socket_udp.sendto(segmento_0, self.direccion_destino)
        debug("Recibiendo respuesta")
        try:
            response_0, incoming_address = self.socket_udp.recvfrom(PACKET_SIZE_MAX)
        except TimeoutError:
            debug("No recibí ningun mensaje por segmento 0")
            return
        parsed_response = self.parse_segment(response_0)
        if parsed_response.seq != self.seq or incoming_address != self.direccion_destino or not parsed_response.ACK:
            debug("No se recibio la respuesta correcta del segmento 0")
            return
        #variables que se actualizan en cada iteración, 
        #constantes para cada iteración
        segment_start = 0
        debug_index = 1
        #pa calcularlo en cada iteración, se actualizan solas, 
        #dependen de las variables de arriba
        segment_end = lambda: segment_start + PACKET_SIZE_MAX #- TCP_HEADER_SIZE
        data = lambda: message[segment_start:segment_end()]
        while data() != b'':
            debug(f"Creando el segmento {debug_index}")
            segmento = self.create_segment(Segment(SYN=False,
                                                   ACK=False,
                                                   FIN=False,
                                                   seq=self.seq,
                                                   data=data()))
            debug(f"Mandando el segmento {debug_index}")
            self.socket_udp.sendto(segmento, self.direccion_destino)
            debug(f"Recibiendo la respuesta del segmento {debug_index}")
            try:
                response, incoming_address = self.socket_udp.recvfrom(PACKET_SIZE_MAX)
            except TimeoutError:
                debug(f"No se recibio la respuesta del segmento {debug_index}")
                return
            parsed_response = self.parse_segment(response)
            segment_start += parsed_response.seq - self.seq #lo que leyó el receptor
            debug(f"El receptor ha leído {segment_start} bytes")
            self.seq = parsed_response.seq
            debug_index += 1
        self.socket_udp.settimeout(None)

    def recv(self, buff_size: int) -> bytes:
        if self.seq==None or self.direccion_destino==None:
            debug("El socket nunca se conectó a algún cliente, abortando recv")
            return bytes()
        self.socket_udp.settimeout(TIMEOUT_TIME)
        #ver si estoy esperando un mensaje nuevo o estoy en proceso de recibir uno
        if self.bytes_left_to_read==0:
            #recibir el segmento 0 para obtener message_length
            debug("Esperando segmento 0")
            try:
                segmento_0, incoming_address = self.socket_udp.recvfrom(PACKET_SIZE_MAX)
            except TimeoutError:
                debug("Nunca me llegó el segmento 0 :(")
                return bytes()
            parsed_segmento_0 = self.parse_segment(segmento_0)
            #message_length
            self.bytes_left_to_read = int(parsed_segmento_0.data.decode())
            self.seq = parsed_segmento_0.seq
            response_0 = self.create_segment(Segment(SYN=False,
                                                     ACK=True,
                                                     FIN=False,
                                                     seq=self.seq,
                                                     data=bytes()))
            self.socket_udp.sendto(response_0, self.direccion_destino)

        packet_size = min(PACKET_SIZE_MAX, buff_size)+TCP_HEADER_SIZE
        message = bytes()
        debug_index = 1
        while len(message)<buff_size:
            debug(f"Esperando el segmento {debug_index}")
            try:
                segmento, incoming_address = self.socket_udp.recvfrom(packet_size)
            except TimeoutError:
                debug(f"Nunca me llegó el segmento {debug_index} :(")
                return message
            parsed_segmento = self.parse_segment(segmento)
            data_read = len(parsed_segmento.data)
            debug(f"Recibí {data_read} bytes de data")
            self.seq += data_read
            message += parsed_segmento.data
            debug(f"El mensaje hasta ahora es {message}")
            self.bytes_left_to_read -= data_read
            debug(f"Me quedan {self.bytes_left_to_read} bytes a leer")
            debug(f"Creando response {debug_index}")
            response = self.create_segment(Segment(SYN=False,
                                                   ACK=True,
                                                   FIN=False,
                                                   seq=self.seq,
                                                   data=bytes()))
            self.socket_udp.sendto(response, self.direccion_destino)
            debug_index += 1
            if self.bytes_left_to_read==0:
                debug("Ya no me quedan bytes pa leer, retornando el wey")
                break
        
        self.socket_udp.settimeout(None)
        debug(f"Retornando {message} con {self.bytes_left_to_read} bytes restantes")
        return message

    def close(self):
        if self.seq == None:
            debug("El socket nunca se conecto a un server, abortando")
            return
        #mandar primer goodbye
        debug("Creando el primer goodbye")
        handshake_1 = self.create_segment(Segment(SYN=True, 
                                                  ACK=False, 
                                                  FIN=False, 
                                                  seq=self.seq, 
                                                  data=bytes()))
        #recibir segundo goodbye

        #mandar tercer goodbye


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