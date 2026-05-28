import argparse
import sys
import SocketTCP

parser = argparse.ArgumentParser(
                    usage="python cliente.py IP puerto [-d, -t, -s, --debug, --test, --stress]",
                    description="Implementación de cliente TCP para la tarea 3 de redes, toma por stdin un mensaje a enviar a la dirección (IP, puerto)",
                    epilog="Hecho con mucho amor por Benjamín Duarte e Ignacio Balbontín"
                    )

parser.add_argument("IP")
parser.add_argument("puerto", type=int)

#modo debug, printea información detallada 
#del funcionamiento interno del socket
parser.add_argument("-d", "--debug", action="store_true")

#activa el test simple, desactiva el stdin, activa el modo debug
parser.add_argument("-t", "--test", action="store_true")

#activa el stress test con 10 sockets, si se activa solo, desactiva el test simple, activa el modo debug
parser.add_argument("-s", "--stress", action="store_true")

args: argparse.Namespace = parser.parse_args()

SocketTCP.DEBUG_FLAG = args.debug or args.test or args.stress

ADDRESS: tuple[str, int] = (args.IP, args.puerto)



if not args.stress and not args.test:
    print("Ingrese mensaje: \n(para terminar, hacer linea nueva y hacer EOF (ctrl+d en linux/mac y ctrl+z en windows))")
    message: bytes = sys.stdin.buffer.read()
    print("Abriendo un SocketTCP")
    s = SocketTCP.SocketTCP()
    print("Conectandose ...")
    s.connect(ADDRESS)
    print(f"Conectado, mandando {message} a {ADDRESS}")
    s.send(message)
    print("Mensaje mandado, cerrando conección")
    s.close()
    print("Conección cerrada")

if args.test:
    print("Abriendo un SocketTCP")
    s = SocketTCP.SocketTCP()
    print("Conectandose ...")
    s.connect(ADDRESS)

    message = "Mensje de len=16".encode()
    s.send(message)
    # test 2
    message = "Mensaje de largo 19".encode()
    s.send(message)
    # test 3
    message = "Mensaje de largo 19".encode()
    s.send(message)

    s.close()

if args.stress:
    print("Recuerde bajar el TIMEOUT_TIME y desactivar el delay para que no sea eterno")
    for i in range(10):
        print(f"------------- Socket {i} -------------")
        s = SocketTCP.SocketTCP()
        s.connect(ADDRESS)
        s.send(f'Hola, soy el socket {i}'.encode())
        _ = s.recv(100)
        s.close()

