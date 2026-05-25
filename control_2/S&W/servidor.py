import socket
import SocketTCP
import argparse

parser = argparse.ArgumentParser(
                    usage="python servidor.py [--d, --debug]",
                    description="Implementación de cliente TCP para la tarea 3 de redes, toma por stdin un mensaje a enviar a la dirección (IP, puerto)",
                    epilog="Hecho con mucho amor por Benjamín Duarte e Ignacio Balbontín"
                    )

parser.add_argument("-d", "--debug", action="store_true")
args: argparse.Namespace = parser.parse_args()
SocketTCP.DEBUG_FLAG = args.debug

print("abriendo socket")
s = SocketTCP.SocketTCP()

IP = "localhost"
PUERTO = 8000
ADDRESS = (IP, PUERTO)

print("binding a la dirección", ADDRESS)
s.bind(ADDRESS)

PACKET_SIZE_MAX = 16

print(f"recibiendo paquetes de tamaño {PACKET_SIZE_MAX}")

try:
    while True:
        print("esperando mensajes...")
        """ 
        incoming_message, incoming_address = s.recvfrom(PACKET_SIZE_MAX)
        segment = SocketTCP.SocketTCP.parse_segment(incoming_message)
        print(f"Se ha recibido el siguiente mensaje con su header:\n {segment}")
         """
        connection_socketTCP, new_address = s.accept()
        print(f"logré establecer conección con {new_address} a través de {connection_socketTCP}")
        connection_socketTCP.socket_udp.close()
        print("---------------------------------------")
finally:
    print("\nCerrando, bye bye")
    s.socket_udp.close()