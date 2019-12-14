import socket
import select


class SocketAPI:
    def __init__(self):
        pass

    @staticmethod
    def get_host():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = '64.233.164.100'
        s.connect((ip, 80))
        return s.getsockname()[0]

    def create(self, source_ip, source_port):
        tcp = socket.getprotobyname("tcp")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, tcp)
        self.sock.bind((source_ip, source_port))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    def send_packet(self, data, address):
        self.sock.sendto(data, address)

    def recv_data(self, timeout):
        s, _, _ = select.select([self.sock], [], [], timeout)
        if s:
            data = s[0].recvfrom(1024)
            return data
        return None

    def close(self):
        self.sock.close()