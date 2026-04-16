class HTTPObject:
    """
    Clase que representa un mensaje http genérico, 

    Puede ser una request o response
    """
    def __init__(self):
        #el start line del mensaje
        self.start_line: bytes = b''

        #el head del mensaje
        self.head: dict(bytes, bytes) = {}

        #el body del mensaje
        self.body: bytes = b''

    def parse(self, raw_str: bytes): #-> HTTPObject
        "parsea un str en bytes, actualizando el objeto"
        head, body = raw_str.split(b"\r\n\r\n", 1)
        #encontramos el start line
        self.start_line: bytes = head.split(b'\r\n')[0]

        #iniciamos un dict para representar el head
        self.head: dict(bytes, bytes) = {}

        #parsear el head (excepto el start line)
        for line_bytes in head.split(b'\r\n')[1:]:
            key, val = line_bytes.split(b":", 1)
            if val.startswith(b" "):
                val = val[1:]
            self.head[key] = val

        #juntamos la lista de bytes del body al original
        self.body: bytes = body

        return self


class HTTPRequest(HTTPObject):
    "Clase que representa un http request"
    def __init__(self):
        HTTPObject.__init__(self)
        self.method: bytes = b''
        self.dir: bytes = b''
        self.version: bytes = b''
    
    def parse(self, raw_str: bytes):
        HTTPObject.__init__(self)
        HTTPObject.parse(self, raw_str)
        start_line_info: bytes = self.start_line.split(b' ')
        self.method: bytes = start_line_info[0]
        self.dir: bytes = start_line_info[1]
        self.version: bytes = start_line_info[2]
        return self

class HTTPResponse(HTTPObject):
    "Clase que representa un http response"
    def __init__(self):
        HTTPObject.__init__(self)
        self.version: bytes = b''
        self.code: bytes = b''
        self.text: bytes = b''

    def parse(self, raw_str: bytes):
        HTTPObject.__init__(self)
        HTTPObject.parse(self, raw_str)
        start_line_info: bytes = self.start_line.split(b" ")
        self.version: bytes = start_line_info[0]
        self.code: bytes = start_line_info[1]
        self.text: bytes = start_line_info[2]
        return self

def parse_http_message(http_message: bytes)-> HTTPObject:
    "Parsea un mensaje http en bytes y lo transforma a su HTTPObject correspondiente"
    start_line: bytes = http_message.split(b'\r\n')[0]
    if start_line.startswith(b'HTTP'):
        return HTTPResponse().parse(http_message)
    else:
        return HTTPRequest().parse(http_message)

def create_http_message(http_obj: HTTPObject)-> bytes:
    "Crea un mensaje http a partir de un objeto HTTP que tenga start_line, head y body"
    http_obj.head[b"Content-Length"] = bytes(str(len(http_obj.body)), encoding="UTF-8")

    message: bytes = b''
    message += http_obj.start_line + b'\r\n'
    for key, val in http_obj.head.items():
        message += key + b': ' + val + b'\r\n'
    message += b'\r\n'
    message += http_obj.body

    return message

if __name__=="__main__":
    example: bytes = b''
    with open("http_example_head_1.txt", encoding="UTF-8") as f:
        for line in f:
            example += bytes(line[:-1], "UTF-8") + b'\r\n'
            print(line)
        f.close()
        example += b'\r\n'

    obj_example= parse_http_message(example)
    print("----start line----")
    print(obj_example.start_line)
    print("----head----")
    print(obj_example.head)
    print("----body----")
    print(obj_example.body)
    print("--------")
    obj_example_2= HTTPResponse()
    obj_example_2.start_line= b'HTTP/1.1 200 OK'
    obj_example_2.head[b"Content-Type"] = b'text/html; charset=UTF-8'
    with open("hello.html", encoding="UTF-8") as body_file:
        obj_example_2.body = bytes(body_file.read(), "UTF-8")
    print(create_http_message(obj_example_2).decode())

