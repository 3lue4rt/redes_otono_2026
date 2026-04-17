import socket
#import dnslib

IP_VM = "localhost"
port = 8000
address = (IP_VM, port)
buffer_size = 4096

print("----------------------------------------------------")
print(f"Dirección: {address}")
print(f"Buffer size: {buffer_size}\n")

print("Creando socket ...\n")
resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"Asociando socket a {address}\n")
resolver_socket.bind(address)

while True:
    print("Esperando mensaje ...")
    incoming_message, _ = resolver_socket.recvfrom(buffer_size)
    print(f"Se ha recibido el siguiente mensaje:\n{incoming_message}\n")