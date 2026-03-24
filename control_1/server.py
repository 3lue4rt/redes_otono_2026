import socket
import http_handling

#CONSTANTES
IP_VM = "192.168.122.197"
port = 8000
vm_address = (IP_VM, port)
buffer_size = 1024

print('Creando socket - Servidor ...')
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("binding ...")
server_socket.bind(vm_address)

print("escuchando hasta 3")
server_socket.listen(3)

while True:
    #accept
    new_socket, new_socket_address = server_socket.accept()

    #recibimos el mensaje
    recv_message = new_socket.recv(buffer_size)
    print(f' -> Se ha recibido el siguiente mensaje: \n{recv_message.decode()}')
    #http_obj: http_handling.HTTPObject = http_handling.parse_http_message(recv_message)
    #cerramos conección
    #new_socket.close()
    #print(f"conexión con {new_socket_address} ha sido cerrada")

