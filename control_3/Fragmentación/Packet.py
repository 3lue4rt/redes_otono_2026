HEADER_SIZE = 16
class Packet:
    def __init__(self, 
                 address: tuple[str, int], 
                 ttl: int, 
                 ID: int, 
                 offset: int,
                 tamano: int,
                 flag: bool,
                 message: bytes) -> None:
        #|IP: 4|Port: 2|TTL: 1|ID: 2|Offset: 2|Tamaño: 4|Flag: 1|Mensaje: Tamaño|
        if not (0 <= ttl <= 255): raise SystemExit(f"Packet({message}): TTL: {ttl} no está en el rango [0, 255]")
        if not (0 <= ID <= 2**16 -1): raise SystemExit(f"Packet({message}): ID: {ID} no está en el rango [0, 2^16 -1]")
        if not (0 <= offset <= 2**16 -1): raise SystemExit(f"Packet({message}): offset:{offset} no está en el rango [0, 2^16 -1]")
        if not (0 <= tamano <= 2**32 -1): raise SystemExit(f"Packet({message}): tamaño:{tamano} no está en el rango [0, 2^32 -1]")
        if not (len(message) == tamano): raise SystemExit(f"Packet({message}): El mensaje no es de tamaño '{tamano}'")
        self.address = address
        self.ttl = ttl
        self.id = ID
        self.offset = offset
        self.tamano = tamano
        self.flag = flag
        self.message = message

    def full_size(self) -> int:
        return HEADER_SIZE + self.tamano

        
    def parseIP(self, IP: str) -> bytes:
        if IP=="localhost":
            IP="127.0.0.1"

        parsed_ints: list[int] = []

        try:
            bytes_list = IP.split(".", maxsplit=3)
            for b in bytes_list:
                parsed_ints.append(int(b))

            return bytes(parsed_ints)
        
        except:
            raise SystemExit(f"Packet: parseAddress: mal formato para {IP}")
    
    def parseAddress(self, address: tuple[str, int]) -> bytes:
        IP, port = address
        return self.parseIP(IP) + self.parsePort(port)
    
    def parsePort(self, port: int) -> bytes:
        return port.to_bytes(length=2)
    
    def parseTTL(self, ttl: int) -> bytes:
        return ttl.to_bytes(length=1)
    
    def parseID(self, id: int) -> bytes:
        return id.to_bytes(length=2)
    
    def parseOffset(self, offset: int) -> bytes:
        return offset.to_bytes(length=2)
    
    def parseTamano(self, tamano: int) -> bytes:
        return tamano.to_bytes(length=4)
    
    def parseHeader(self) -> bytes:
        address = self.parseAddress(self.address)
        ttl = self.parseTTL(self.ttl)
        id = self.parseID(self.id)
        offset = self.parseOffset(self.offset)
        tamano = self.parseTamano(self.tamano)
        return address + ttl + id + offset + tamano + self.flag.to_bytes()
    
    def to_bytes(self) -> bytes:
        return self.parseHeader() + self.message
    
    def __str__(self) -> str:
        return f"{self.address[0]};{self.address[1]};{self.ttl};{self.id};{self.offset};{self.tamano};{self.flag};{self.message}"
    
# |IP: 4|Port: 2|TTL: 1|ID: 2|Offset: 2|Tamaño: 4|Flag: 1|Mensaje: Tamaño|
# tamaños en bytes
def parse_packet(IP_packet: bytes) -> Packet:
    try:
        raw_IP, raw_port = IP_packet[0:4], IP_packet[4:6]
        raw_TTL, raw_ID = IP_packet[6], IP_packet[7:9]
        raw_offset, raw_tamano = IP_packet[9:11], IP_packet[11:15]
        raw_flag, raw_message = IP_packet[15], IP_packet[16:]
    except:
        raise SystemExit(f"Packet: parseAddress: mal formato para {IP_packet}")
    
    IP = ""
    for b in raw_IP:
        IP += str(b) + "."
    IP = IP[:-1]

    port = int.from_bytes(raw_port)
    id = int.from_bytes(raw_ID)
    offset = int.from_bytes(raw_offset)
    tamano = int.from_bytes(raw_tamano)
    flag = bool(raw_flag)

    return Packet(address=(IP, port),
                  ttl=raw_TTL,
                  ID=id,
                  offset=offset,
                  tamano=tamano,
                  flag=flag,
                  message=raw_message)


def create_packet(parsed_IP_packet: Packet) -> bytes:
    return parsed_IP_packet.to_bytes()

def fragment_IP_packet(IP_packet: Packet, MTU: int) -> list[Packet]:
    if IP_packet.full_size()<=MTU: return [IP_packet]
    #else
    fragments: list[Packet] = []
    address = IP_packet.address #constante
    ttl = IP_packet.ttl #constante
    id = IP_packet.id #constante
    offset = IP_packet.offset #lo actualizamos a medida que se fragmenta
    flag = IP_packet.flag #despues lo revisamos
    msg = IP_packet.message #lo actualizamos a medida que se fragmenta

    while msg != b'':
        length = MTU - HEADER_SIZE #tamaño del paquete maximo
        msg_fragment = msg[:length] #da lo mismo si len(msg)<length
        fragments.append(Packet(address,
                                ttl,
                                id,
                                offset,
                                len(msg_fragment),
                                True, #despues vemos si es el final del paquete
                                msg_fragment))
        offset += length #se actualiza el offset para los siguientes fragmentos
        msg = msg[length:] #le cortamos el fragmento ya empaquetado

    if not flag:
        fragments[-1].flag = False
    
    return fragments

def reassemble_IP_packet(fragment_list: list[Packet]) -> Packet | None:
    #ordenamos la lista según el offset
    fragment_list.sort(key=lambda p: p.offset)
    #si el último fragmento no es el último o el
    #primero no es el primero, no se puede rearmar
    if fragment_list[-1].flag or fragment_list[0].offset != 0:
        return None
    #vamos armando el fragmento, si vemos alguna inconsistencia, abortamos
    result = fragment_list.pop(0)
    offset = result.offset + result.tamano
    for fragment in fragment_list:
        #inconsistencias conn los paquetes
        if fragment.id != result.id or fragment.offset != offset:
            return None
        #si todo está bien, actualizamos el resultado final
        result.tamano += fragment.tamano
        result.message += fragment.message
        #actualizamos el offset global para seguir el orden
        offset += fragment.tamano

    result.flag = False
    return result



if __name__=="__main__":
    #test 4
    IP_packet_v1 = Packet(address=('localhost', 8000), 
                          ttl=49,
                          ID=100,
                          offset=0,
                          tamano=4,
                          flag=False,
                          message=b'Hola').to_bytes()
    parsed_IP_packet = parse_packet(IP_packet_v1)
    IP_packet_v2 = create_packet(parsed_IP_packet)
    print(f"{IP_packet_v1} == {IP_packet_v2} ? {IP_packet_v1 == IP_packet_v2}")

    msg = b"Hola, esto es un mensaje bien largo, como estas?, yo muy bien, gracias, el MTU debe ser mayor a 16, o si no el header no cabe en el paquete :O, bueno creo que este largo es suficiente."
    packet_og = Packet(address=('localhost', 8000), 
                          ttl=255,
                          ID=56,
                          offset=0,
                          tamano=len(msg),
                          flag=False,
                          message=msg)
    assert(fragment_IP_packet(packet_og, 1000) == [packet_og])

    fragments = [Packet(address=('localhost', 8000), 
                        ttl=255,
                        ID=56,
                        offset=0,
                        tamano=50,
                        flag=True,
                        message=b'Hola, esto es un mensaje bien largo, como estas?, '),
                 Packet(address=('localhost', 8000), 
                        ttl=255,
                        ID=56,
                        offset=50,
                        tamano=50,
                        flag=True,
                        message=b'yo muy bien, gracias, el MTU debe ser mayor a 16, '),
                 Packet(address=('localhost', 8000), 
                        ttl=255,
                        ID=56,
                        offset=100,
                        tamano=50,
                        flag=True,
                        message=b'o si no el header no cabe en el paquete :O, bueno '),
                 Packet(address=('localhost', 8000), 
                        ttl=255,
                        ID=56,
                        offset=150,
                        tamano=34,
                        flag=False,
                        message=b'creo que este largo es suficiente.')]
    fragments_fun = fragment_IP_packet(packet_og, HEADER_SIZE + 50)
    for i in range(4):
        assert(fragments_fun[i].address == fragments[i].address)
        assert(fragments_fun[i].ttl == fragments[i].ttl)
        assert(fragments_fun[i].id == fragments[i].id)
        assert(fragments_fun[i].offset == fragments[i].offset)
        assert(fragments_fun[i].tamano == fragments[i].tamano)
        assert(fragments_fun[i].flag == fragments[i].flag)
        assert(fragments_fun[i].message == fragments[i].message)
    
    fragment_list = fragment_IP_packet(packet_og, 50)
    packet_og_v2 = reassemble_IP_packet(fragment_list)
    if packet_og_v2:
        print(f"{packet_og} == {packet_og_v2} ? {packet_og.to_bytes() == packet_og_v2.to_bytes()}")
    else:
        print("packet_og_v2 es None")