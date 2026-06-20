class Packet:
    def __init__(self, address: tuple[str, int], ttl: int, message: bytes) -> None:
        self.address = address
        if not (0 <= ttl <= 255): raise SystemExit("TTL no está en el rango [0, 255]")
        self.ttl = ttl
        self.message = message
        self.header = self.parseAddress(address) + self.parseTTL(ttl)
        
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
        
    
    def parsePort(self, port: int) -> bytes:
        return port.to_bytes(length=2)
    
    def parseTTL(self, ttl: int) -> bytes:
        return ttl.to_bytes()
    
    def parseAddress(self, address: tuple[str, int]) -> bytes:
        IP, port = address
        return self.parseIP(IP) + self.parsePort(port)
    
    def to_bytes(self) -> bytes:
        return self.parseAddress(self.address) + self.parseTTL(self.ttl) + self.message
    
    def __str__(self) -> str:
        return f"{self.address[0]};{self.address[1]};{self.ttl};{self.message}"
    

def parse_packet(IP_packet: bytes) -> Packet:
    try:
        raw_IP, raw_port, ttl, raw_msg = IP_packet[0:4], IP_packet[4:6], IP_packet[6], IP_packet[7:]
    except:
        raise SystemExit(f"Packet: parseAddress: mal formato para {IP_packet}")
    
    IP = ""
    for b in raw_IP:
        IP += str(b) + "."
    IP = IP[:-1]

    port = int.from_bytes(raw_port)

    return Packet(address=(IP, port),
                  ttl=ttl,
                  message=raw_msg)


def create_packet(parsed_IP_packet: Packet) -> bytes:
    return parsed_IP_packet.to_bytes()


if __name__=="__main__":
    #test 4
    IP_packet_v1 = Packet(address=('localhost', 8000), ttl=49, message=b'ola').to_bytes()
    parsed_IP_packet = parse_packet(IP_packet_v1)
    IP_packet_v2 = create_packet(parsed_IP_packet)
    print(f"{IP_packet_v1} == {IP_packet_v2} ? {IP_packet_v1 == IP_packet_v2}")