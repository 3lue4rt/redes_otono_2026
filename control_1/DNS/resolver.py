import socket
import parseDNS
from dnslib import DNSRecord

IP_VM = "localhost"
root_address = ("192.33.4.12", 53)
port = 8000
address = (IP_VM, port)
buffer_size = 4096
show_debug = True
cache = []
last_doms = []

print("----------------------------------------------------")
print(f"Dirección: {address}")
print(f"Buffer size: {buffer_size}")
print(f"Modo Debug: {show_debug}")
print("----------------------------------------------------\n")

print("Creando socket ...\n")
resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"Asociando socket a {address}\n")
resolver_socket.bind(address)

## PENDIENTE
def add_to_cache(dns_result: bytes):
    parsed = parseDNS.DNSObj(dns_result)
    last_doms.append((str(parsed.Qname), str(parsed.Answer[0].RDATA)))
    if len(last_doms)>20:
        last_doms.pop(0)

    # Source - https://stackoverflow.com/a/23240989
    # Posted by sshashank124, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-04-17, License - CC BY-SA 4.0
    count = {dom:last_doms.count(dom) for dom in last_doms}

    # Source - https://stackoverflow.com/a/280156
    # Posted by A. Coady
    # Retrieved 2026-04-17, License - CC BY-SA 2.5
    highest = max(count, key=count.get)


    



def debug(msg):
    "print para debuguear, depende de la variable global show_debug"
    if show_debug:
        print(msg)

def resolver(mensaje_consulta: bytes) -> bytes:
    "resolver DNS"
    #parseamos la consulta
    parsed_message = parseDNS.DNSObj(mensaje_consulta)
    debug(f"Se ha recibido el siguiente mensaje de consulta:\n{parsed_message}")

    #a.- hacemos la query al servidor raíz 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(mensaje_consulta, root_address)
        data, _ = sock.recvfrom(4096)
        answer = parseDNS.DNSObj(data)
        debug(f"Se obtuvo la respuesta del servidor raíz:\n{answer}")
    finally:
        sock.close()
    
    while True:
        #b.- si hay answers, buscamos si hay alguna de tipo A
        if answer.ANCOUNT>0:
            for answer_rr in answer.Answer:
                if "A"==answer_rr.TYPE:
                    debug(f"Encontré la siguiente ip en Answers: {answer_rr.RDATA}")
                    debug("Enviando respuesta final")
                    return data
        
        #c.- si vienen respuestas NS
        if answer.NSCOUNT>0:
            # busco primero en Additionals si hay tipo A
            answer_in_additional = False
            for additional_rr in answer.Additional:
                # i.- se encuentra un tipo A
                if "A"==additional_rr.TYPE:
                    debug(f"Encontré la siguiente ip en Additional: {additional_rr.RDATA}")
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    try:
                        sock.sendto(mensaje_consulta, (str(additional_rr.RDATA), 53))
                        data, _ = sock.recvfrom(4096)
                        answer = parseDNS.DNSObj(data)
                        debug(f"Se obtuvo una respuesta de {additional_rr.RDATA}:\n{answer}")
                        answer_in_additional = True
                    finally:
                        sock.close()
                    break

            if not answer_in_additional:
                debug("No encontré respuesta en additional, cambiando Name Server")
                # tomo el nombre de un NS y lo resuelvo recursivamente
                new_query = resolver(bytes(DNSRecord.question(str(answer.Qname)).pack()))
                # sacamos la ip de la resolución
                new_ip = parseDNS.DNSObj(new_query).Answer[0].RDATA
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    sock.sendto(mensaje_consulta, (new_ip, 53))
                    data, _ = sock.recvfrom(4096)
                    answer = parseDNS.DNSObj(data)
                    debug(f"Se obtuvo una respuesta de {new_ip}:\n{answer}")
                finally:
                    sock.close()


        #d.- Ignoramos si no hay en answers ni authority
        else:
            debug("No encontré respuesta :(")
            return


        
while True:
    print("Esperando nuevo mensaje ...")
    incoming_message, incoming_address = resolver_socket.recvfrom(buffer_size)
    print("Ocupando el resolver ...")
    response = resolver(incoming_message)
    resolver_socket.sendto(response, incoming_address)
    print("Request resuelto\n\n\n")
    
