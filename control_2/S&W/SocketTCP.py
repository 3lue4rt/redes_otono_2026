import socket
from random import randint

DEBUG_FLAG = False
TCP_HEADER_SIZE = 2 #bytes
PACKET_SIZE_MAX = 16 + TCP_HEADER_SIZE #bytes
TIMEOUT_TIME = 2 #segundos
CONNECTION_TIME = 1 #segundos
MAX_TRIES = 3 #intentos antes de rendirse (deprecado)

#función debugueadora, printea si el DEBUG_FLAG es True
debug_counter = 1
def debug(msg: object):
    global debug_counter
    print(f"({debug_counter})", msg) if DEBUG_FLAG else None
    debug_counter+=1

class SocketTCP:
    "Implementación de juguete de un socket TCP orientado a conección"
    def __init__(self):
        debug("Creando socket UDP")
        self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #Dirección al socket TCP de destino (distinto al address de connect())
        self.direccion_destino: tuple[str, int] | None  = None
        #Dirección a la que se bindea el socket
        self.direccion_origen: tuple[str, int] | None = None
        #N° de secuencia, si es None significa que no se ha conectado o
        #que ya se cerró la conección
        self.seq: int | None = None
        #N° que indíca la cantidad de bytes que le queda al socket
        #por leer de un mensaje a medio recibir.
        self.bytes_left_to_read: int = 0

    @staticmethod
    def parse_segment(segment: bytes) -> Segment:
        "Toma un segmento de PACKET_SIZE_MAX bytes y lo transforma en una instancia de Segment"
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
        #CONSIDERANDO EL BIT DE MÁS A LA IZQ COMO EL ÚLTIMO
        byte1 = segment[0]
        byte2 = segment[1]
        data = segment[2:]
        #shift 7 derecha nos da el último bit
        SYN = bool(byte1 >> 7)
        #shift 6 derecha y solo obtenemos el primer bit
        ACK = bool((byte1 >> 6) & 1)
        #shift 5 derecha y solo obtenemos el primer bit
        FIN = bool((byte1 >> 5) & 1)
        #los 13 bits sobrantes son nuestro n° de secuencia (rango 0-8191)
        seq = ((byte1 & (2**5 -1)) << 8) + byte2
        ret = Segment(SYN, ACK, FIN, seq, data)
        debug(ret)
        return ret
    
    @staticmethod
    def create_segment(segment: Segment) -> bytes:
        "Toma una instancia de Segment y devuelve un segmento de PACKET_SIZE_MAX bytes"
        debug(f"Creando segmento {segment}")
        #Reconstruimos el byte 1 tal como lo desarmamos, aprovechamos que True==1 y False==0
        byte1 = segment.SYN*(2**7) + segment.ACK*(2**6) + segment.FIN*(2**5) + (segment.seq >> 8)
        #Byte 2 es bastante directo, los primeros 8 bits del n° de secuencia
        byte2 = segment.seq & (2**8 - 1)
        return bytes([byte1, byte2]) + segment.data

    def bind(self, address: tuple[str, int]):
        "El socket escucha en la dirección address"
        self.direccion_origen = address
        debug(f"El socket queda bindeado a la dirección {address}")
        self.socket_udp.bind(address)

    def connect(self, address: tuple[str, int]):
        "El SocketTCP se conecta con otro SocketTCP en la dirección address usando el 3-way handshake"
        #inicializamos el n° de secuencia inicial
        self.seq = randint(0, 100)

        #mandar el primer hanshake y esperamos el segundo
        handshake_1_tries = 1 #contamos los intentos solo para debuguear
        #tenemos timeout para todo el resto del connect()
        self.socket_udp.settimeout(TIMEOUT_TIME)

        debug("Creando el primer handshake")
        handshake_1 = self.create_segment(Segment(SYN=True, 
                                                  ACK=False, 
                                                  FIN=False, 
                                                  seq=self.seq, 
                                                  data=bytes()))
        
        while True:

            debug(f"Mandando el primer hanshake (intento {handshake_1_tries})")
            self.socket_udp.sendto(handshake_1, address)

            try:
                #segundo handshake
                debug("Recibiendo el segundo handshake")
                handshake_2, incoming_address = self.socket_udp.recvfrom(TCP_HEADER_SIZE)

            except TimeoutError:
                debug(f"Se demoró mucho el handshake 2")
                handshake_1_tries += 1
                continue #mandando el handshake 1

            debug("Logré recibir el segundo handshake, parseando ...")
            parsed_shake = self.parse_segment(handshake_2)

            #si no es el handshake 2 o el n° de secuencia no coincide
            if not parsed_shake.is_handshake_2() or parsed_shake.seq != self.seq+1:
                debug("No era el segundo handshake, intentando de nuevo")
                handshake_1_tries += 1
                continue
            else:
                self.seq = parsed_shake.seq + 1
                debug(f"Segundo handshake en orden, actualizando el n° de secuencia {self.seq}")
                break
        else:
            #deprecated
            debug(f"ya llegué a {MAX_TRIES} intentos, abortando el handshake 1")
            self.seq = None
            return

        #se que me llegó el handshake 2, actualizo el n° de secuencia
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

        debug(f"Ahora me comunico con {incoming_address} (ojalá, se confirma en el send())")
        self.direccion_destino = incoming_address
        self.direccion_origen = self.socket_udp.getsockname()

    def accept(self) -> tuple[SocketTCP, tuple[str, int]]:
        "El socketTCP acepta la conección de un SocketTCP 's', retornando otro SocketTCP y la dirección de s"
        #sin timeout, podemos esperar clientes para siempre
        self.socket_udp.settimeout(None)

        #esperamos el primer handshake
        while True:

            debug("Recibiendo el primer handshake (tiempo infinito de espera)")
            handshake_1, incoming_address = self.socket_udp.recvfrom(TCP_HEADER_SIZE)

            debug("Recibí un segmento, parseando ...")
            parsed_shake = self.parse_segment(handshake_1)

            if not parsed_shake.is_handshake_1():
                debug("No era el primer handshake, empezando de nuevo")
                continue
            else:
                self.seq = parsed_shake.seq + 1
                debug(f"Primer handshake en orden, actualizando el n° de secuencia {self.seq}")
                break
        
        #mandamos el segundo handshake con el nuevo socket
        debug("Creando el segundo handshake")
        handshake_2 = self.create_segment(Segment(SYN=True, 
                                                  ACK=True, 
                                                  FIN=False, 
                                                  seq=self.seq, 
                                                  data=bytes()))
        
        #nuevo socket para la comunicación
        new_sock = SocketTCP()
        #El nuevo socket no es tan paciente como el servidor...
        new_sock.socket_udp.settimeout(TIMEOUT_TIME)

        handshake_2_tries = 1 #solo debug
        #Sigo mandando el handshake 2 hasta recibir el 3
        while True:

            debug(f"Enviando el segundo handshake con el nuevo socket (intento {handshake_2_tries})")
            new_sock.socket_udp.sendto(handshake_2, incoming_address)
            #esperamos el tercer handshake
            
            try:
                handshake_3, incoming_address = new_sock.socket_udp.recvfrom(TCP_HEADER_SIZE)
                debug("Recibiendo el tercer handshake")
                
            except TimeoutError:
                debug("Se demoró demasiado el handshake 3, mandando el 2 de nuevo")
                handshake_2_tries += 1
                continue

            debug("Logré recibir el tercer handshake, parseando ...")
            parsed_shake = self.parse_segment(handshake_3)

            #si no es el handshake 3 o el n° de secuencia no coincide
            if not parsed_shake.is_handshake_3() or parsed_shake.seq != self.seq+1:
                debug("No era el tercer handshake, intentando de nuevo")
                handshake_2_tries += 1
                continue
            else:
                self.seq = parsed_shake.seq
                debug(f"Tercer handshake en orden, actualizando el n° de secuencia {self.seq}")
                break
        else:
            #deprecated
            debug(f"Ya llegué a {MAX_TRIES} intentos, abortando y volviendo al handshake 1")
            self.seq = None
            return self.accept()
        
        #el nuevo socket estará encargado de la comunicación
        #con el cliente de ahora en adelante, lo dejamos seteado
        new_sock.seq = parsed_shake.seq
        new_sock.direccion_destino = incoming_address
        new_sock.direccion_origen = new_sock.socket_udp.getsockname()
        return new_sock, incoming_address

    def send(self, message: bytes):
        """ 
        El SocketTCP manda un mensaje en bytes al servidor que se conectó,
        si no se ha conectado, termina de inmediato. """
        if self.seq==None or self.direccion_destino==None:
            debug("El socket nunca se conectó a algún servidor, abortando send")
            return
        
        #Timeouts por si no habían
        self.socket_udp.settimeout(TIMEOUT_TIME)

        debug(f"Enviando a {self.direccion_destino}\nTamaño máximo de paquete {PACKET_SIZE_MAX} bytes")

        #Mandando el segmento 0 (que contiene el largo del mensaje)
        message_length = len(message)
        debug(f"Leído el siguiente mensaje:\n{message}\n Largo: {message_length}")
        debug("Creando segmento 0 con el largo del mensaje")
        segmento_0 = self.create_segment(Segment(SYN=False,
                                                 ACK=False,
                                                 FIN=False,
                                                 seq=self.seq,
                                                 data=str(message_length).encode()))
        
        #manejamos el caso en donde el servidor no recibió el handshake 3
        while True:
            debug("Mandando segmento 0")
            self.socket_udp.sendto(segmento_0, self.direccion_destino)
            debug("Recibiendo respuesta")
            try:
                debug("Recibiendo respuesta")
                response_0, _ = self.socket_udp.recvfrom(PACKET_SIZE_MAX)
            except TimeoutError:
                debug("No recibí ningun mensaje por segmento 0")
                continue
            debug(f"Recibí respuesta, parseando ...")
            parsed_response = self.parse_segment(response_0)

            #si no recibió el handshake 2 hay que mandar el 3 y el segmento 0
            if parsed_response.is_handshake_2:
                debug("Recibí el 2do handshale (OH NO)")
                debug("Creando el tercer handshake")
                handshake_3 = self.create_segment(Segment(SYN=False, 
                                                        ACK=True, 
                                                        FIN=False, 
                                                        seq=self.seq, 
                                                        data=bytes()))
                debug("Mandando el tercer handshake")
                self.socket_udp.sendto(handshake_3, self.direccion_destino)
                continue
            if parsed_response.is_ack_message() and parsed_response==self.seq + message_length:
                debug("El segmento 0 fue recibido, empezando a mandar el mensaje")
                self.seq = parsed_response.seq
                break
        
        #variables que se actualizan en cada iteración
        segment_start = 0
        debug_index = 1
        #variable que dependen de las de arriba, 
        #se actualizan solas al llamar el lambda
        segment_end = lambda: segment_start + PACKET_SIZE_MAX
        data = lambda: message[segment_start:segment_end()]

        #mandamos el mensaje hasta que no nos quede más por mandar
        while data() != b'':

            debug(f"Creando el segmento {debug_index}")
            segmento = self.create_segment(Segment(SYN=False,
                                                   ACK=False,
                                                   FIN=False,
                                                   seq=self.seq,
                                                   data=data()))
            
            #mandamos el segmento hasta que llegue un ACK
            while True:
                debug(f"Mandando el segmento {debug_index}")
                self.socket_udp.sendto(segmento, self.direccion_destino)

                try:
                    debug(f"Recibiendo la respuesta del segmento {debug_index}")
                    response, _ = self.socket_udp.recvfrom(PACKET_SIZE_MAX)

                except TimeoutError:
                    debug(f"No se recibio la respuesta del segmento {debug_index}")
                    continue

                debug("Recibí  una respuesta, parseando ...")
                parsed_response = self.parse_segment(response)

                if parsed_response.is_ack_message():
                    segment_start += parsed_response.seq - self.seq #lo que leyó el receptor
                    debug(f"El receptor ha leído {segment_start} bytes")
                    self.seq = parsed_response.seq
                    debug_index += 1
                    break

                else:
                    debug("No era una respuesta ACK")
                    continue

        debug("El receptor recibió el mensaje completo")
        #desactivamos el timeout
        self.socket_udp.settimeout(None)

    def recv(self, buff_size: int) -> bytes:
        """ 
        El SocketTCP recibe un mensaje en bytes del cliente que se conectó,
        recibiendo a lo más buff_size bytes,
        si no se ha conectado, termina de inmediato. """
        if self.seq==None or self.direccion_destino==None:
            debug("El socket nunca se conectó a algún cliente, abortando recv")
            return bytes()
        
        #Espera infinito por el segmento 0
        self.socket_udp.settimeout(None)
        
        #ver si estoy esperando un mensaje nuevo o estoy en proceso de recibir uno
        #recibir el segmento 0 para obtener message_length
        while True:
            debug("Esperando segmento 0")
            segmento_0, _ = self.socket_udp.recvfrom(PACKET_SIZE_MAX)
            debug("LLegó un segmento, parseando ...")
            parsed_segmento_0 = self.parse_segment(segmento_0)

            #si coincidimos en el n° de seq y estoy esperando el segmento 0
            if parsed_segmento_0.is_std_message() and parsed_segmento_0.seq==self.seq:
                debug("Me llegó el segmento 0")
                #message_length
                self.bytes_left_to_read = int(parsed_segmento_0.data.decode())

                debug(f"Tengo que leer {self.bytes_left_to_read} bytes")
                self.seq = parsed_segmento_0.seq
                response_0 = self.create_segment(Segment(SYN=False,
                                                        ACK=True,
                                                        FIN=False,
                                                        seq=self.seq,
                                                        data=bytes()))
                self.socket_udp.sendto(response_0, self.direccion_destino)

            if parsed_segmento_0.is_std_message() and parsed_segmento_0.seq<self.seq:
                debug("Ya recibí el segmento 0, pero el receptor no recibió respuesta")
                response_0 = self.create_segment(Segment(SYN=False,
                                                         ACK=True,
                                                         FIN=False,
                                                         seq=self.seq,
                                                         data=bytes()))
                self.socket_udp.sendto(response_0, self.direccion_destino)
                debug("Mandando respuesta del segmento 0 hasta que llegue")
                while True:
                    self.socket_udp.sendto(response_0, self.direccion_destino)
                    segmento, _ = self.socket_udp.recvfrom(PACKET_SIZE_MAX)
                    parsed_segmento = self.parse_segment(segmento)
                    if parsed_segmento.is_std_message() and parsed_segmento.seq==self.seq:
                        debug("Logramos coincidir")
                        #aquí mandamos una ACK dicendo que no leimos nada, a la proxima leemos algo con las siguientes iteraciones
                        self.socket_udp.sendto(response_0, self.direccion_destino)
                        break
                break

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
        if self.seq == None or self.direccion_destino==None:
            debug("El socket nunca se conecto a un server, abortando")
            return
        #mandar primer goodbye
        debug("Creando el primer goodbye")
        goodbye_1 = self.create_segment(Segment(SYN=False, 
                                                ACK=False, 
                                                FIN=True, 
                                                seq=self.seq, 
                                                data=bytes()))
        debug("Mandando el primer goodbye")
        self.socket_udp.sendto(goodbye_1, self.direccion_destino)
        #recibir segundo goodbye
        debug("Recibiendo el segundo goodbye")
        goodbye_2, incoming_address = self.socket_udp.recvfrom(TCP_HEADER_SIZE)
        parsed_bye = self.parse_segment(goodbye_2)
        #aquí verificar que el parsed goodbye es correcto
        # ...
        self.seq = parsed_bye.seq + 1
        #mandar tercer goodbye
        debug("Creando el tercer goodbye")
        goodbye_3 = self.create_segment(Segment(SYN=False, 
                                                ACK=True, 
                                                FIN=False, 
                                                seq=self.seq, 
                                                data=bytes()))
        self.socket_udp.sendto(goodbye_3, self.direccion_destino)
        #deleteamos el seq y la dirección
        self.seq = None
        self.direccion_destino = None
        debug("He cerrado la connección del lado del cliente")

    def recv_close(self):
        if self.seq == None or self.direccion_destino==None:
            debug("El socket no está conectado a un server, abortando")
            return
        #recibir primer goodbye
        debug("Recibiendo el primer goodbye")
        goodbye_1, incoming_address = self.socket_udp.recvfrom(TCP_HEADER_SIZE)
        parsed_bye = self.parse_segment(goodbye_1)
        self.seq = parsed_bye.seq + 1
        #mandar el segundo goodbye
        debug("Creando el segundo goodbye")
        goodbye_1 = self.create_segment(Segment(SYN=False, 
                                                ACK=True, 
                                                FIN=True, 
                                                seq=self.seq, 
                                                data=bytes()))
        debug("Mandando el segundo goodbye")
        self.socket_udp.sendto(goodbye_1, self.direccion_destino)
        #recibir el tercer goodbye
        debug("Recibiendo el tercer goodbye")
        goodbye_3, incoming_address = self.socket_udp.recvfrom(TCP_HEADER_SIZE)
        parsed_bye = self.parse_segment(goodbye_3)
        self.seq = None
        self.direccion_destino = None
        debug("He cerrado la connección del lado del servidor")



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
    
    def is_handshake_1(self):
        return self.SYN and not self.ACK and not self.FIN
    
    def is_handshake_2(self):
        return self.SYN and self.ACK and not self.FIN
    
    def is_handshake_3(self):
        return self.is_ack_message()
    
    def is_std_message(self):
        return not (self.SYN or self.ACK or self.FIN)
    
    def is_ack_message(self):
        return not self.SYN and self.ACK and not self.FIN
    
    def is_goodbye_1(self):
        return not self.SYN and not self.ACK and self.FIN
    
    def is_goodbye_2(self):
        return not self.SYN and self.ACK and self.FIN
    
    def is_goodbye_3(self):
        return self.is_ack_message()