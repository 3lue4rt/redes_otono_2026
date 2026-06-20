import argparse
import socket
import Packet
from sys import stdin

USAGE = "python3 prueba_router.py headers IP_router_inicial puerto_router_inicial"
DESCRIPTION = """Manda un archivo recibido por stdin a la dirección definida por <headers> desde
el router con dirección (IP_router_inicial, puerto_router_inicial)
"""
EPILOG = "Hecho con mucho amor por Benjamín Duarte e Ignacio Balbontín"

parser = argparse.ArgumentParser(
                    usage=USAGE,
                    description=DESCRIPTION,
                    epilog=EPILOG
                    )

parser.add_argument("headers")
parser.add_argument("IP_router_inicial")
parser.add_argument("puerto_router_inicial", type=int)

args: argparse.Namespace = parser.parse_args()

INITIAL_ADDRESS: tuple[str, int]= (args.IP_router_inicial, args.puerto_router_inicial)

raw_ip, raw_port, raw_ttl = args.headers.split(";")

FINAL_ADDRESS = (raw_ip, int(raw_port))

ttl = int(raw_ttl)

print("ingrese el mensaje: ")
msgs = stdin.buffer.read().split(b'\n')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for msg in msgs:
    packet = Packet.Packet(address=FINAL_ADDRESS,ttl=ttl, message=msg).to_bytes()
    s.sendto(packet, INITIAL_ADDRESS)

s.close()