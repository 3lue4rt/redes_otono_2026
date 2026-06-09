class Packet:
    def __init__(self, address: tuple[str, int], message: bytes) -> None:
        self.address = address
        self.message = message
        self.header = self.parseAddress(address)
        
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
    

    def parseAddress(self, address: tuple[str, int]) -> bytes:
        IP, port = address
        return self.parseIP(IP) + b';' + self.parsePort(port)
    
    def to_bytes(self) -> bytes:
        return self.header + b';' + self.message
    
    def __str__(self) -> str:
        return f"{self.address[0]};{self.address[1]};{self.message}"
    

def parse_packet(IP_packet: bytes) -> Packet:
    try:
        raw_IP, raw_port, raw_msg = IP_packet.split(b';')
    except:
        raise SystemExit(f"Packet: parseAddress: mal formato para {IP_packet}")
    
    IP = ""
    for b in raw_IP:
        IP += str(b) + "."
    IP = IP[:-1]

    port = int.from_bytes(raw_port)

    return Packet(address=(IP, port),
                  message=raw_msg)


def create_packet(parsed_IP_packet: Packet) -> bytes:
    return parsed_IP_packet.to_bytes()


if __name__=="__main__":
    #test 4
    IP_packet_v1 = Packet(address=('localhost', 8000), message=b'ola').to_bytes()
    parsed_IP_packet = parse_packet(IP_packet_v1)
    IP_packet_v2 = create_packet(parsed_IP_packet)
    print(f"{IP_packet_v1} == {IP_packet_v2} ? {IP_packet_v1 == IP_packet_v2}")