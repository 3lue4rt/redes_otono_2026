import argparse
import socket
import Packet
from random import randint

USAGE = "python sender.py IP_inicio puerto_inicio IP_final puerto_final"
DESCRIPTION = """Manda un mensaje por stdin desde (IP_inicio, puerto_inicio) hacia (IP_final, puerto_final)
"""
EPILOG = "Hecho con mucho amor por Benjamín Duarte e Ignacio Balbontín"

parser = argparse.ArgumentParser(
                    usage=USAGE,
                    description=DESCRIPTION,
                    epilog=EPILOG
                    )

parser.add_argument("IP_inicio")
parser.add_argument("puerto_inicio", type=int)
parser.add_argument("IP_final")
parser.add_argument("puerto_final", type=int)

args: argparse.Namespace = parser.parse_args()

INITIAL_ADDRESS: tuple[str, int]= (args.IP_inicio, args.puerto_inicio)
FINAL_ADDRESS: tuple[str, int]= (args.IP_final, args.puerto_final)

msg = input("ingrese el mensaje: ")

print(f"largo del mensaje: {len(msg)}")

ttl = None
while True:
    ttl = input("ingrese el ttl: ")
    try:
        ttl = int(ttl)
        if not (0 <= ttl <= 255): raise Exception
        else: break
    except:
        print("ttl no válido, intente de nuevo")

id = None
while True:
    id = input("ingrese el id: ")
    try:
        id = int(id)
        if not (0 <= id <= 2**16-1): raise Exception
        else: break
    except:
        print("id no válido, intente de nuevo")


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

packet = Packet.Packet(address=FINAL_ADDRESS,
                       ttl=ttl,
                       ID=id,
                       offset=0,
                       tamano=len(msg),
                       flag=False,
                       message=msg.encode()).to_bytes()

s.sendto(packet, INITIAL_ADDRESS)

s.close()