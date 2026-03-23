import socket

#CONSTANTES
IP_VM = "192.168.122.1"
port = 80
vm_address = (IP_VM, port)
buffer_size = 1024

print("creando socket ...")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("connectando al server ...")
client_socket.connect(vm_address)
print("conectado")

abierto = True
while abierto:
    mensaje = input("mensaje: ")
    if mensaje=="exit":
        abierto=False
        
    client_socket.send(mensaje.encode())

    recibido = client_socket.recv(buffer_size)
    print(f"mensaje del servidor:\n {recibido}")

print("cerrando conección ...")
client_socket.close()
print("chao")