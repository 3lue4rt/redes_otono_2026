import socket

#CONSTANTES
IP_VM = "192.168.122.197"
port = 80
vm_address = (IP_VM, port)
buffer_size = 1024



abierto = True
while abierto:
    print("creando socket ...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("connectando al server ...")
    client_socket.connect(vm_address)
    print("conectado")

    mensaje = input("mensaje: ")

    if mensaje=="exit":
        abierto=False

    client_socket.send(mensaje.encode())
    print("cerrando conección ...")
    client_socket.close()
print("chao")