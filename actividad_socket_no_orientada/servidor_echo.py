import socket

print("abriendo socket")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = ('localhost', 5000)

print("binding a la dirección", address)
s.bind(address)

buff_size = 1
end_of_message = "\n"

print("recibiendo un buffer de tamaño", buff_size)

print("esperando mensajes...")

print("----------------------------")
print("el primer recvfrom:")
incoming_message, incoming_address = s.recvfrom(buff_size)
print(incoming_message)
print(incoming_address)
print("el segundo recvfrom:")
incoming_message, incoming_address = s.recvfrom(buff_size)
print(incoming_message)
print(incoming_address)
print(f' -> Se ha recibido el siguiente mensaje: {incoming_message}')
print("fin\n")