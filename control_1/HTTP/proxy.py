import socket
import http_handling
import json

#CONSTANTES
#ip del proxy, cambiar según usuario al ejecutar proxy.py
IP_VM = "localhost"
port = 8000
vm_address = (IP_VM, port)
buffer_size = 64

#aquí guardaremos los settings
settings = {
    "user": b'',
    "blocked": [],
    "forbidden_words": []
}

#toma un socket O.A.C. ya conectado y se asegura de recibir el mensaje completo
def recieve_message(s: socket.socket) -> bytes:
    "toma un socket O.A.C. ya conectado y se asegura de recibir el mensaje completo"
    msg = s.recv(buffer_size)
    bytes_read = buffer_size

    while b'\r\n\r\n' not in msg:
        buffer = s.recv(buffer_size)
        msg += buffer
        bytes_read += len(buffer)
        print(f"leyendo {bytes_read} bytes hasta encontrar \\r\\n\\r\\n")
    head = msg.split(b'\r\n\r\n', 1)[0] + b'\r\n\r\n'
    
    #si es un request no necesitamos body
    if not head.split(b'\r\n')[0].startswith(b"HTTP"):
        return head
    
    body_read = bytes_read - len(head)
    print(f"he leído {body_read} bytes del body hasta ahora")

    leyendo = True
    while leyendo:
        buffer = s.recv(buffer_size)
        msg += buffer
        body_read += len(buffer)
        print(f"he leído {len(buffer)} bytes nuevos del body")
        if len(buffer)<buffer_size:
            leyendo = False

    print("Mensaje leído")
    return msg

#toma un body en bytes y reemplaza todas las
#palabras prohibídas por su reemplazo
def filter_body(body: bytes) -> bytes:
    for word_replace in settings["forbidden_words"]:
        for original in word_replace:
            body = bytes(body.decode().replace(original, word_replace[original]), "UTF-8")
    return body

#maneja un request segun la direccion pedida
def handle_request(http_req: http_handling.HTTPRequest)-> http_handling.HTTPResponse:
    "maneja un request de cliente"
    if http_req.dir==b'/':
        return handle_request_internal(http_req)
    else:
        return handle_request_external(http_req)

#maneja un request al root del proxy
def handle_request_internal(_)-> http_handling.HTTPResponse:
    "maneja los request internos y entrega un html default"
    #creamos un HTTPResponse pelao
    response = http_handling.HTTPResponse()

    #agregamos su start_line
    response.start_line = b'HTTP/1.1 200 OK'

    #agregamos a su head el content type
    response.head[b"Content-Type"] = b'text/html; charset=UTF-8'

    #agregamos el body
    with open("hello.html", encoding="UTF-8") as body:
        response.body = bytes(body.read(), "UTF-8")
    
    return response

#maneja un request externo al proxy, revisa
#si el sitio está bloqueado
def handle_request_external(http_req: http_handling.HTTPRequest) -> http_handling.HTTPResponse:
    "maneja cuando llega un request para conectarse a un servidor externo"
    print("tratando de conectar a", http_req.dir.decode())

    #si es un sitio bloqueado
    if http_req.dir.decode() in settings["blocked"]:
        print("conexion prohibida")
        response = http_handling.HTTPResponse()
        response.start_line = b'HTTP/1.1 403 Forbidden'
        response.head[b"Content-Type"] = b'text/html; charset=UTF-8'
        response.head[b'Server'] = b'Proxy'
        with open("prohibited.html", encoding="UTF-8") as body:
            response.body = bytes(body.read(), "UTF-8")
            return response

    print("conexion permitida")
    #creamos el socket hacia el servidor externo
    external_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #nos conectamos
    external_socket.connect((http_req.head[b"Host"], 80))
    #enviamos lo que nos pasaron + un header especial
    http_req.head[b'X-ElQuePregunta'] = bytes(settings["user"], "UTF-8")
    external_socket.send(http_handling.create_http_message(http_req))
    #recibimos la respuesta y la parseamos
    response = recieve_message(external_socket)
    external_socket.close()

    return http_handling.parse_http_message(response)

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

print('Creando socket - Proxy ...')
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("binding ...")
proxy_socket.bind(vm_address)

print("escuchando hasta 3")
proxy_socket.listen(3)

while True:
    #aceptamos un cliente
    client_socket, client_socket_address = proxy_socket.accept()

    #recibimos el mensaje
    recv_message = recieve_message(client_socket)
    print(f' -> Se ha recibido el siguiente mensaje: \n{recv_message.decode()}')
    http_request = http_handling.parse_http_message(recv_message)

    print("Manejando request ...")
    http_response = handle_request(http_request)
    http_response.body = filter_body(http_response.body)
    byte_response = http_handling.create_http_message(http_response)

    print("enviando el siguiente mensaje:")
    print(byte_response.decode())
    client_socket.send(byte_response)
    print("Response enviada")

    #cerramos conección con el cliente
    client_socket.close()
