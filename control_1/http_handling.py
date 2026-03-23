class HTTPObject:
    """
    Clase que representa un mensaje http genérico, 

    Puede ser una request o response
    """
    def __init__(self, raw_str: bytes):
        self.raw: bytes = raw_str
        self.line_list: list(bytes) = self.raw.split(b'\r\n')
        separator: int = self.line_list.index(b'')
        self.head: list(bytes) = self.line_list[:separator]
        self.body: list(bytes) = self.line_list[separator:]
        

class HTTPRequest(HTTPObject):
    "Clase que representa un http request"
    def __init__(self, raw_str: bytes):
        HTTPObject.__init__(self, raw_str)

class HTTPResponse(HTTPObject):
    "Clase que representa un http response"
    def __init__(self, raw_str: bytes):
        HTTPObject.__init__(self, raw_str)

def parse_http_message(http_message: bytes)-> HTTPObject:
    "Parsea un mensaje http en bytes y lo transforma a su HTTPObject correspondiente"
    start_line: bytes = http_message.split(b'\r\n')[0]
    if start_line.startswith(b'HTTP'):
        return HTTPResponse(http_message)
    else:
        return HTTPRequest(http_message)


# crea un mensaje http a partir de un objeto http
def create_http_message(http_obj: HTTPObject)-> bytes:
    "Crea un mensaje http a partir de un objeto HTTP"
    ...

example: bytes = b''
with open("http_example_head_1.txt", encoding="UTF-8") as f:
    for line in f:
        example += bytes(line[:-1], "UTF-8") + b'\r\n'
        print(line)
    f.close()
    example += b'\r\n'
    print(example)

obj_example= HTTPObject(example)
print(obj_example.line_list)
