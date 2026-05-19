import socket
import argparse
import sys
import time

parser = argparse.ArgumentParser(
                    usage="python cliente.py IP puerto [--d, --debug]",
                    description="Implementación de cliente TCP para la tarea 3 de redes, toma por stdin un mensaje a enviar a la dirección (IP, puerto)",
                    epilog="Hecho con mucho amor por Benjamín Duarte e Ignacio Balbontín"
                    )

parser.add_argument("IP")
parser.add_argument("puerto", type=int)
parser.add_argument("-d", "--debug", action="store_true")
args: argparse.Namespace = parser.parse_args()

def debug(msg):
    print(msg) if args.debug else None

ADDRESS: tuple[str, int] = (args.IP, args.puerto)
PACKET_SIZE_MAX = 16

debug(f"Enviando a {ADDRESS}\nTamaño máximo de paquete {PACKET_SIZE_MAX} bytes")

message: bytes = sys.stdin.buffer.read()

debug(f"Leído el siguiente mensaje:\n{message}")

debug(f"Descomponiendo el mensaje en paquetes de {PACKET_SIZE_MAX} bytes")

# Source - https://stackoverflow.com/a/22571377
# Posted by Tim Zimmermann
# Retrieved 2026-05-19, License - CC BY-SA 3.0

paquetes = [message[i:i+PACKET_SIZE_MAX] for i in range(0, len(message), PACKET_SIZE_MAX)]

if len(paquetes)>=3:
    debug(f"Los primeros 3 paquetes son {paquetes[0:3]}")
else:
    debug(f"Los paquetes a enviar son {paquetes}")

debug(f"abriendo un socket UDP")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    debug(f"Enviando paquetes...")
    for paquete in paquetes:
        debug(f"Enviando {paquete} a las {time.time()}")
        s.sendto(paquete, ADDRESS)
finally:
    s.close()

