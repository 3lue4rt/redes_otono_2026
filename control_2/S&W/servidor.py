import SocketTCP
import argparse

parser = argparse.ArgumentParser(
                    usage="python servidor.py [-d, -t, -s, --debug, --test, --stress]",
                    description="Implementación de servidor TCP para la tarea 3 de redes, se bindea a (localhost, 8000)",
                    epilog="Hecho con mucho amor por Benjamín Duarte e Ignacio Balbontín"
                    )

#modo debug, printea información detallada 
#del funcionamiento interno del socket
parser.add_argument("-d", "--debug", action="store_true")

#activa el test simple, desactiva el stdin, activa el modo debug
parser.add_argument("-t", "--test", action="store_true")

#activa el stress test con 10 sockets, si se activa solo desactiva el test simple, activa el modo debug
parser.add_argument("-s", "--stress", action="store_true")

args: argparse.Namespace = parser.parse_args()

SocketTCP.DEBUG_FLAG = args.debug or args.test or args.stress

IP = "localhost"
PUERTO = 8000
ADDRESS = (IP, PUERTO)

print("abriendo server")
s = SocketTCP.SocketTCP()
print("binding a la dirección", ADDRESS)
s.bind(ADDRESS)

if not args.stress and not args.test:
    print("Esperando cliente ...")
    connection_socketTCP, new_address = s.accept()
    print(f"Conectado, recibiendo mensaje de {new_address}")
    connection_socketTCP.recv(100)
    print("Mensaje recibido, cerrando conección")
    connection_socketTCP.recv_close()
    print("Conección cerrada")

if args.test:

    connection_socketTCP, new_address = s.accept()

    # test 1
    buff_size = 16
    full_message = connection_socketTCP.recv(buff_size)
    print("Test 1 received:", full_message)
    if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
    else: print("Test 1: Failed")

    # test 2
    buff_size = 19
    full_message = connection_socketTCP.recv(buff_size)
    print("Test 2 received:", full_message)
    if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
    else: print("Test 2: Failed")

    # test 3
    buff_size = 14
    message_part_1 = connection_socketTCP.recv(buff_size)
    message_part_2 = connection_socketTCP.recv(buff_size)
    print("Test 3 received:", message_part_1 + message_part_2)
    if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
    else: print("Test 3: Failed")

if args.stress:
    print("Recuerde bajar el TIMEOUT_TIME para que no sea eterno")
    for i in range(10):
        print(f"------------- Socket {i} -------------")
        connection_socketTCP, new_address = s.accept()
        _ = connection_socketTCP.recv(100)
        connection_socketTCP.send(f'Adiós socket {i}, nos vemos'.encode())
        connection_socketTCP.recv_close()
