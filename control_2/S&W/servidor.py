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

connection_socketTCP, new_address = s.accept()

# test 1
buff_size = 16
full_message = connection_socketTCP.recv(buff_size)
print("Test 1 received:", full_message)
if full_message == "Mensje de len=16".encode(): 
    print("Test 1: Passed")
else: 
    print("Test 1: Failed")

# test 2
buff_size = 19
full_message = connection_socketTCP.recv(buff_size)
print("Test 2 received:", full_message)
if full_message == "Mensaje de largo 19".encode():
    print("Test 2: Passed")
else: 
    print("Test 2: Failed")

# test 3
buff_size = 14
message_part_1 = connection_socketTCP.recv(buff_size)
message_part_2 = connection_socketTCP.recv(buff_size)
print("Test 3 received:", message_part_1 + message_part_2)
if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): 
    print("Test 3: Passed")
else: 
    print("Test 3: Failed")

