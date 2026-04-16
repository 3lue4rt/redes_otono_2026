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
        #separamos el head del body
        head, self.body = raw_str.split(b"\r\n\r\n", 1)

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

        
        return self


class HTTPRequest(HTTPObject):
    "Clase que representa un http request"
    def __init__(self):
        #init del objeto
        HTTPObject.__init__(self)
        #metodo del start line
        self.method: bytes = b''
        #direccion pedida
        self.dir: bytes = b''
        #version del http
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
        #version del http
        self.version: bytes = b''
        #codigo del mensaje
        self.code: bytes = b''
        #texto del mensaje
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
    #medimos el body
    http_obj.head[b"Content-Length"] = bytes(str(len(http_obj.body)), encoding="UTF-8")

    message: bytes = b''

    #agregamos el start line
    message += http_obj.start_line + b'\r\n'
    
    #agregamos el head
    for key, val in http_obj.head.items():
        message += key + b': ' + val + b'\r\n'
    message += b'\r\n'

    #agregamos el body
    message += http_obj.body

    return message
