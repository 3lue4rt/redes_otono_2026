from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib

class RR:
    def __init__(self):
        self.NAME = None
        self.TYPE = None
        self.CLASS = None
        self.TTL = None
        #self.RDLENGTH = None
        self.RDATA = None

    def parse(self, rr: dnslib.dns.RR) -> None:
        "Dado un RR le asigna a sus variables los datos correspondientes"
        self.NAME = rr.get_rname()
        self.TYPE = QTYPE.get(rr.rtype)
        self.CLASS = CLASS.get(rr.rclass)
        self.TTL = rr.ttl
        #self.RDLENGTH = rr.rdlength
        self.RDATA = rr.rdata

    def __str__(self):
        name = f"NAME: {self.NAME}\n"
        type_ = f"TYPE: {self.TYPE}\n"
        class_ = f"CLASS: {self.TYPE}\n"
        ttl = f"TTL: {self.TTL}\n"
        #rdlength = f"RDLENGTH: {self.RDLENGTH}\n"
        rdata = f"RDATA: {self.RDATA}\n"
        return name + type_ + class_ + ttl + rdata

class DNSObj:
    def __init__(self):
        self.Qname = None
        self.ANCOUNT = None
        self.NSCOUNT = None
        self.ARCOUNT = None
        self.Answer = RR()
        self.Authority = RR()
        self.Additional = RR()

    def parse(self, dns_message_bytes: bytes) -> None:
        "Dado un DNSRecord le asigna a sus variables los datos correspondientes"
        dns_message = DNSRecord.parse(dns_message_bytes)
        self.Qname = dns_message.get_q().get_qname()
        self.ANCOUNT = dns_message.header.a
        self.NSCOUNT = dns_message.header.auth
        self.ARCOUNT = dns_message.header.ar
        if self.ANCOUNT>0:
            self.Answer.parse(dns_message.get_a())
        if self.NSCOUNT>0:
            self.Authority.parse(dns_message.auth[0])
        if self.ARCOUNT>0:
            self.Additional.parse(dns_message.ar[0])

    def __str__(self):
        sep = "------------------------------\n"
        Qname = f"Qname: {self.Qname}\n"
        ANCOUNT = f"ANCOUNT: {self.ANCOUNT}\n"
        NSCOUNT = f"NSCOUNT: {self.NSCOUNT}\n"
        ARCOUNT = f"ARCOUNT: {self.ARCOUNT}\n\n"
        answer = f"Answer:\n{self.Answer}\n"
        auth = f"Authority:\n{self.Authority}\n"
        additional = f"Additional Records:\n{self.Additional}"
        return sep + Qname + ANCOUNT + NSCOUNT + ARCOUNT + answer + auth + additional + sep

if __name__=="__main__":
    example = DNSObj()
    print(example)