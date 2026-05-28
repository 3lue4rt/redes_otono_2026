import argparse
import sys
import SocketTCP

parser = argparse.ArgumentParser(
                    usage="python cliente.py IP puerto [--d, --debug]",
                    description="Implementación de cliente TCP para la tarea 3 de redes, toma por stdin un mensaje a enviar a la dirección (IP, puerto)",
                    epilog="Hecho con mucho amor por Benjamín Duarte e Ignacio Balbontín"
                    )

parser.add_argument("IP")
parser.add_argument("puerto", type=int)
parser.add_argument("-d", "--debug", action="store_true")
args: argparse.Namespace = parser.parse_args()

SocketTCP.DEBUG_FLAG = args.debug

def debug(msg: object):
    print(msg) if args.debug else None

ADDRESS: tuple[str, int] = (args.IP, args.puerto)

debug(f"Enviando a {ADDRESS}:")
message: bytes = sys.stdin.buffer.read()

debug(f"abriendo un 'socket' TCP")
s = SocketTCP.SocketTCP()
s.connect(ADDRESS)
s.send(message)
s.close()

""" #Stress test
print("EMPEZANDO EL STRESS TEST")
for i in range(10):
    print(f"-------------SOCKET N°{i}--------------")
    s = SocketTCP.SocketTCP()
    s.connect(ADDRESS)
    s.send(f'ola, soy el socket {i}'.encode())
    s.close() """