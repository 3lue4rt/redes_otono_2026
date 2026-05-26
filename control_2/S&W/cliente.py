import socket
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

debug(f"Enviando a {ADDRESS}")

message: bytes = sys.stdin.buffer.read()

debug(f"abriendo un 'socket' TCP")
s = SocketTCP.SocketTCP()

try:
    """ debug(f"Enviando paquetes...")
    for paquete in paquetes:
        debug(f"Enviando {SocketTCP.SocketTCP.parse_segment(paquete)}")
        s.sendto(paquete, ADDRESS) """
    s.connect(ADDRESS)
    # test 1
    message = "Mensje de len=16".encode()
    s.send(message)
    # test 2
    message = "Mensaje de largo 19".encode()
    s.send(message)
    # test 3
    message = "Mensaje de largo 19".encode()
    s.send(message)
finally:
    s.socket_udp.close()
