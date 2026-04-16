import socket
import http_handling
import json

#CONSTANTES
IP_VM = "localhost"
port = 8000
vm_address = (IP_VM, port)
buffer_size = 1024
settings = {
    "user": b'',
    "blocked": [],
    "forbidden_words": []
}

# leer los settings
if __name__=="__main__":
    with open("settings.json", encoding="UTF-8") as file:
        settings = json.load(file)

        print("Usuario:", settings["user"])

        print("Páginas bloqueadas:")
        for site in settings["blocked"]:
            print("-", site)

        print("Palabras prohibídas:")
        for word in settings["forbidden_words"]:
            for key in word:
                print("-", key)
        
        file.close()

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
    http_obj: http_handling.HTTPObject = http_handling.parse_http_message(recv_message)

    #por mientras para ver si funciona
    if http_obj.start_line.startswith(b'GET') or http_obj.start_line.startswith(b'HEAD'):
        new_socket.send(http_handling.handle_request(http_obj, settings))
    #cerramos conección

    new_socket.close()
    #print(f"conexión con {new_socket_address} ha sido cerrada")

