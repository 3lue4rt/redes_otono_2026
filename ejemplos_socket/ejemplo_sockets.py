import socket

#orientado a conexión
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#no orientado a conexión
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
