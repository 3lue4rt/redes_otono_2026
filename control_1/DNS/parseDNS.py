from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
from dnslib.label import DNSLabel
import dnslib

class RR:
    def __init__(self, rr: dnslib.dns.RR):
        self.NAME: DNSLabel = rr.get_rname()
        self.TYPE: str = QTYPE.get(rr.rtype)
        self.CLASS: str = CLASS.get(rr.rclass)
        self.TTL: int = rr.ttl
        #self.RDLENGTH = None
        self.RDATA: dnslib.dns.A | dnslib.dns.AAAA = rr.rdata

    def __str__(self):
        name = f"NAME: {self.NAME}\n"
        type_ = f"TYPE: {self.TYPE}\n"
        class_ = f"CLASS: {self.TYPE}\n"
        ttl = f"TTL: {self.TTL}\n"
        #rdlength = f"RDLENGTH: {self.RDLENGTH}\n"
        rdata = f"RDATA: {self.RDATA}\n"
        return name + type_ + class_ + ttl + rdata

class DNSObj:
    def __init__(self, dns_message_bytes: bytes):

        dns_message = DNSRecord.parse(dns_message_bytes)

        self.Qname = dns_message.get_q().get_qname()

        header = dns_message.header
        self.ID: int = header.id
        self.ANCOUNT: int = header.a
        self.NSCOUNT: int = header.auth
        self.ARCOUNT: int = header.ar

        self.Answer: list[RR] = []
        if self.ANCOUNT>0:
            for answer_rr in dns_message.rr:
                self.Answer += [RR(answer_rr)]

        self.Authority: list[RR] = []
        if self.NSCOUNT>0:
            for authority_rr in dns_message.auth:
                self.Authority += [RR(authority_rr)]

        self.Additional: list[RR] = []
        if self.ARCOUNT>0:
            for additional_rr in dns_message.ar:
                self.Additional += [RR(additional_rr)]

    def __str__(self):
        sep = "------------------------------\n"
        ID = f"ID: {self.ID}\n"
        Qname = f"Qname: {self.Qname}\n"
        ANCOUNT = f"ANCOUNT: {self.ANCOUNT}\n"
        NSCOUNT = f"NSCOUNT: {self.NSCOUNT}\n"
        ARCOUNT = f"ARCOUNT: {self.ARCOUNT}\n\n"
        answer = f"1 de {self.ANCOUNT} Answer:\n{self.Answer[0]}\n" if self.ANCOUNT>0 else ""
        auth = f"1 de {self.NSCOUNT} Authority:\n{self.Authority[0]}\n" if self.NSCOUNT>0 else ""
        additional = f"1 de {self.ARCOUNT} Additional Records:\n{self.Additional[0]}" if self.ARCOUNT>0 else ""
        return sep + ID + Qname + ANCOUNT + NSCOUNT + ARCOUNT + answer + auth + additional + sep
