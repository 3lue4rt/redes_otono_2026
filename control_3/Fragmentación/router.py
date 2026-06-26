import argparse
import socket
import Packet
import time

USAGE = "python router.py router_IP router_puerto router_rutas [FLAGS]"
DESCRIPTION = """Simula un router que escucha desde (router_IP, router_puerto) y tiene la tabla de rutas router_rutas
"""
EPILOG = "Hecho con mucho amor por Benjamín Duarte e Ignacio Balbontín"

parser = argparse.ArgumentParser(
                    usage=USAGE,
                    description=DESCRIPTION,
                    epilog=EPILOG
                    )

parser.add_argument("router_IP")
parser.add_argument("router_puerto", type=int)
parser.add_argument("router_rutas")

parser.add_argument("-d", "--debug", action="store_true")

args: argparse.Namespace = parser.parse_args()

class RouteTableLine:
    def __init__(self, line: str) -> None:
        self.line = line
        self.red_CIDR, \
        puerto_inicial, \
        puerto_final, \
        self.ip_destino, \
        puerto_destino, \
        mtu = line.split()

        self.puerto_inicial = int(puerto_inicial)
        self.puerto_final = int(puerto_final)
        self.puerto_destino = int(puerto_destino)
        self.mtu = int(mtu)

    def CIDRrange(self) ->set[str]:
        ip, mask = self.red_CIDR.split("/")
        #por mientras tenemos un solo ip
        return {ip}

    def inPortRange(self, port) -> bool:
        return self.puerto_inicial <= port <= self.puerto_final

    def check_route(self, address: tuple[str, int]) -> tuple[tuple[str, int], int] | None:
        ip, port = address
        if ip in self.CIDRrange() and self.inPortRange(port):
            return (self.ip_destino, self.puerto_destino), self.mtu

    def __str__(self) -> str:
        return self.line

    def __repr__(self) -> str:
        return str(self)


class RouteTable:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.table: list[RouteTableLine] = []
        with open(file_name) as table:
            for line in table:
                self.table.append(RouteTableLine(line[:-1]))
        self.cache: dict[tuple[str, int], list[RouteTableLine]] = {}
        for line in self.table:
            for ip in line.CIDRrange():
                for port in range(line.puerto_inicial, line.puerto_final +1):
                    if (ip, port) not in self.cache.keys():
                        self.cache[(ip, port)] = [line]
                    else:
                        self.cache[(ip, port)].append(line)


    def check_routes(self, destination_address: tuple[str, int]) -> tuple[tuple[str, int], int] | None:
        result = None
        if destination_address in self.cache.keys():
            result = self.cache[destination_address][0].check_route(destination_address)
            temp = self.cache[destination_address].pop(0)
            self.cache[destination_address].append(temp)
        else:
            print(f"no existe la llave en el cache {destination_address}")
            print(self.cache.keys())
        return result

ROUTETABLE = RouteTable(args.router_rutas)    

def check_routes(_: str, 
                 destination_address: tuple[str, int])-> tuple[tuple[str, int], int] | None:
    return ROUTETABLE.check_routes(destination_address)

routerIP = "127.0.0.1" if args.router_IP=="localhost" else args.router_IP

fragment_dict: dict[int, list[Packet.Packet]] = {}

ADDRESS: tuple[str, int]= (routerIP, args.router_puerto)
        
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

s.bind(ADDRESS)

BUFFER_SIZE = 10000

print(f"Iniciando router, escuchando en {ADDRESS}")

while True:

    print("Esperando paquetes ...")
    msg, _ = s.recvfrom(BUFFER_SIZE)
    packet = Packet.parse_packet(msg)
    if packet.ttl<=0:
        print("======================================")
        print(f"Se recibió paquete {packet} con TTL 0")
        print("======================================")

    elif packet.address == ADDRESS:
        
        if packet.id in fragment_dict.keys():
            fragment_dict[packet.id].append(packet)
        else:
            fragment_dict[packet.id] = [packet]

        reensamble_try = Packet.reassemble_IP_packet(fragment_dict[packet.id])
        if reensamble_try:
            print(f"Recibí el siguiente mensaje: \n{reensamble_try.message}")
            del fragment_dict[packet.id] #ya recibimos el paquete completo, borramos los fragmentos
        else:
            print(f"Llegó el fragmento {packet.offset} al {packet.offset + packet.tamano}, \npero todavía no tengo el paquete completo")

    else:
        next_hop_mtu = check_routes(args.router_rutas, packet.address)

        if next_hop_mtu:
            next_hop, mtu = next_hop_mtu
            fragment_list = Packet.fragment_IP_packet(packet, mtu)

            for fragment in fragment_list:
                fragment.ttl -= 1
                print(f"Redirigiendo paquete [{fragment}]\n con destino final {fragment.address}\ndesde {ADDRESS} hacia {next_hop}")
                s.sendto(fragment.to_bytes(), next_hop)
        else:
            print(f"No hay rutas hacia {packet.address} para paquete \n[{packet}]")
