import socket

print("creamos socket")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

buffer_size = 1024
print(f"buffer de {buffer_size}")

address = ('localhost', 5000)

s.sendto("abc".encode(), address)

print("enviando...")

print("------------------------------------------")
    