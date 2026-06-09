import argparse
import socket
import Packet

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

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

packet = Packet.Packet(address=FINAL_ADDRESS, message=msg.encode()).to_bytes()

s.sendto(packet, INITIAL_ADDRESS)

s.close()