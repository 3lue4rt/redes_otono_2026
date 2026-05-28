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

IP = "localhost"
PUERTO = 8000
ADDRESS = (IP, PUERTO)

print("abriendo socket")
s = SocketTCP.SocketTCP()

print("binding a la dirección", ADDRESS)
s.bind(ADDRESS)

""" connection_socketTCP, new_address = s.accept()
_ = connection_socketTCP.recv(501)
_ = connection_socketTCP.recv(501)
connection_socketTCP.recv_close() """

for i in range(1000):
    print(f"-------------SOCKET N°{i}--------------")
    connection_socketTCP, new_address = s.accept()
    print(f"Socket {i} conectado")
    print(f"Socket {i} recibió: {connection_socketTCP.recv(100)}")
    connection_socketTCP.recv_close()
    print(f"Socket {i} cerrado")