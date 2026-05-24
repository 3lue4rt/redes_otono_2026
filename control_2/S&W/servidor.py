import socket
import SocketTCP

print("abriendo socket")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
        incoming_message, incoming_address = s.recvfrom(PACKET_SIZE_MAX)
        segment = SocketTCP.SocketTCP.parse_segment(incoming_message)
        print(f"Se ha recibido el siguiente mensaje con su header:\n {segment}")
        print("---------------------------------------")
finally:
    print("\nCerrando, bye bye")
    s.close()