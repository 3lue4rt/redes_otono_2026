import socket
import parseDNS
from dnslib import DNSRecord
from dnslib.dns import RR, QTYPE, A

IP_VM = "localhost"
root_address = ("192.33.4.12", 53)
port = 8000
address = (IP_VM, port)
buffer_size = 4096
show_debug = True
cache = {}
last_doms = []
max_items_in_cache = 3
last_doms_length = 20

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
def update_cache(dns_result: parseDNS.DNSObj) -> None:
    "dado una respuesta dns actualiza el cache con las consultas más frecuentes"
    last_doms.append((str(dns_result.Qname), str(dns_result.Answer[0].RDATA)))
    if len(last_doms)>last_doms_length:
        last_doms.pop(0)

    # Source - https://stackoverflow.com/a/23240989
    # Posted by sshashank124, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-04-17, License - CC BY-SA 4.0
    count = {dom:last_doms.count(dom) for dom in last_doms}

    #limpiamos el cache
    cache.clear()

    while count != {} and len(cache) < max_items_in_cache:
        # Source - https://stackoverflow.com/a/280156
        # Posted by A. Coady
        # Retrieved 2026-04-17, License - CC BY-SA 2.5
        highest = max(count, key=count.get)
        cache[highest[0]] = highest[1]
        count.pop(highest)



def debug(msg):
    "print para debuguear, depende de la variable global show_debug"
    if show_debug:
        print("(debug)", msg)

def resolver(mensaje_consulta: bytes) -> bytes:
    "resolver DNS"
    
    #parseamos la consulta
    parsed_message = parseDNS.DNSObj(mensaje_consulta)
    debug(f"Se ha recibido el siguiente mensaje de consulta:\n{parsed_message}")

    #revisamos el caché
    debug(f"Revisando cache por {parsed_message.Qname}")
    if str(parsed_message.Qname) in cache:
        ip = cache[str(parsed_message.Qname)]
        debug(f"Encontré el ip {ip} para el dominio {parsed_message.Qname}")
        response_cache = DNSRecord.parse(mensaje_consulta)
        response_cache.add_answer(RR(parsed_message.Qname, QTYPE.A, rdata=A(ip)))
        debug(f"actualizando el caché con ({parsed_message.Qname}: {ip})")
        update_cache(parseDNS.DNSObj(response_cache.pack()))
        debug(f"respondiendo con el siguiente mensaje:\n{parseDNS.DNSObj(response_cache.pack())}")
        return response_cache.pack()

    #a.- hacemos la query al servidor raíz 
    debug("No se encontró en el cache, consultando al servidor raíz ...")
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
                    debug(f"actualizando el caché con ({parsed_message.Qname}: {answer_rr.RDATA})")
                    update_cache(parseDNS.DNSObj(data))
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
    debug(f"cache: {cache}")
    debug(f"Últimos {last_doms_length} dominios consultados:\n{last_doms}")
    print("Esperando nuevo mensaje ...")
    incoming_message, incoming_address = resolver_socket.recvfrom(buffer_size)
    print("Ocupando el resolver ...")
    response = resolver(incoming_message)
    resolver_socket.sendto(response, incoming_address)
    print("Request resuelto\n\n\n")
    
