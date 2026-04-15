class HTTPObject:
    """
    Clase que representa un mensaje http genérico, 

    Puede ser una request o response
    """
    def __init__(self, raw_str: bytes):
        #string pelao en bytes
        self.raw: bytes = raw_str 

        #lista de lineas del http
        self.line_list: list(bytes) = self.raw.split(b'\r\n')

        #buscamos el doble salto de línea
        separator: int = self.line_list.index(b'')

        #separamos head y body
        self.head_list_bytes: list(bytes) = self.line_list[:separator]
        self.body_list_bytes: list(bytes) = self.line_list[separator+1:]

        #encontramos el start line
        self.start_line: bytes = self.head_list_bytes[0]

        #iniciamos un dict para representar el head
        self.head: dict(bytes, bytes) = {}

        #parsear el head (excepto el start line)
        for line_bytes in self.head_list_bytes[1:]:
            key, val = line_bytes.split(b":", 1)
            if val.startswith(b" "):
                val = val[1:]
            self.head[key] = val

        #juntamos la lista de bytes del body al original
        self.body: bytes = self.body_list_bytes[0]

class HTTPRequest(HTTPObject):
    "Clase que representa un http request"
    def __init__(self, raw_str: bytes):
        HTTPObject.__init__(self, raw_str)
        start_line_info: bytes = self.start_line.split(b' ')
        self.method: bytes = start_line_info[0]
        self.dir: bytes = start_line_info[1]
        self.version: bytes = start_line_info[2]


class HTTPResponse(HTTPObject):
    "Clase que representa un http response"
    def __init__(self, raw_str: bytes):
        HTTPObject.__init__(self, raw_str)
        start_line_info: bytes = self.start_line.split(" ")
        self.version: bytes = start_line_info[0]
        self.code: bytes = start_line_info[1]
        self.text: bytes = start_line_info[2]

def parse_http_message(http_message: bytes)-> HTTPObject:
    "Parsea un mensaje http en bytes y lo transforma a su HTTPObject correspondiente"
    start_line: bytes = http_message.split(b'\r\n')[0]
    if start_line.startswith(b'HTTP'):
        return HTTPResponse(http_message)
    else:
        return HTTPRequest(http_message)

def create_http_message(http_obj: HTTPObject)-> bytes:
    "Crea un mensaje http a partir de un objeto HTTP"
    message: bytes = b''
    message += http_obj.start_line + b'\r\n'
    for key, val in http_obj.head.items():
        message += key + b': ' + val + b'\r\n'
    message += http_obj.body
    return message

def handle_request(http_req: HTTPRequest)-> bytes:
    "crea un mensaje de respuesta para GET o HEAD"
    head: bytes = b''
    body: bytes = b''
    body_length: int = 0
    with open("hello.html", encoding="UTF-8") as f_body:
        body: bytes = bytes(f_body.read(), "UTF-8")
        body_length = len(body)
        f_body.close()

        #:v

    #ocupamos un head default
    with open("http_example_head_1.txt", encoding="UTF-8") as f_head:
        for head_line in f_head:
            if head_line.startswith("Content-Length:"):
                head_line = head_line[:-1] + str(body_length) + '\n'
            head += bytes(head_line[:-1], "UTF-8") + b'\r\n'

        head += b'X-ElQuePregunta: Benjamin Duarte'
        f_head.close()
    head += b'\r\n'

    if http_req.method == b'HEAD':
        return head
    elif http_req.method == b'GET':
        return head+body

if __name__=="__main__":
    example: bytes = b''
    with open("http_example_head_1.txt", encoding="UTF-8") as f:
        for line in f:
            example += bytes(line[:-1], "UTF-8") + b'\r\n'
            print(line)
        f.close()
        print("--------")
        example += b'\r\n'

    obj_example= HTTPObject(example)
    print(obj_example.head)
    print(obj_example.body)
