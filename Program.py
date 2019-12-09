import socket
import time
import select
import Creator
import sys
import Parcer
import Statistics


class Program:
    def __init__(self, source_addr, address, params, stats, mode):
        self.source_ip, self.source_port = source_addr
        self.source_ip = self.get_ip()
        self.address = address
        self.count, self.timeout, self.interval = params
        self.is_unlimited_mode = mode

        self.packets = {}
        self.count_of_packets_sent = 0
        self.count_of_received_packets = 0
        self.seq = 10

        self.stats = Statistics.StatManager()
        for stat in stats:
            self.stats.add_statistics(stat)

    @staticmethod
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = socket.gethostbyname('e1.ru')
        s.connect((ip, 80))
        return s.getsockname()[0]

    def create_socket(self):
        tcp = socket.getprotobyname("tcp")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, tcp)
        self.sock.bind((self.source_ip, self.source_port))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        

    def send_packet(self):
        for addr in self.address:
            packet = Creator.HeaderCreator(
                self.source_ip, addr[0],
                self.source_port, addr[1], self.seq)
            self.packets[self.seq] = packet
            self.sock.sendto(packet.make_SYN_query(), addr)
            t = time.perf_counter()
            packet.send_time = t
            self.count_of_packets_sent += 1
            sys.stdout.write('.')
            sys.stdout.flush()
            self.seq += 10

    def parse_packet(self, data, recv_time):
        parser = Parcer.Parser(data[0])
        if parser.proto != 6:
            return
        if parser.filter_by_addr_list(self.address):
            seq = parser.ack - 1
            if seq in self.packets.keys():
                self.packets[seq].is_answered = True
                self.packets[seq].answer_time = recv_time
                self.packets[seq].time = recv_time - \
                    self.packets[seq].send_time
                if self.packets[seq].time < self.timeout:
                    self.count_of_received_packets += 1
                    self.stats.update(self.packets[seq])
                    sys.stdout.write('*')
                    sys.stdout.flush()
                else:
                    self.packets_loss += 1
                    sys.stdout.write('_')
                    sys.stdout.flush()

    def send_and_receive_packets(self):
        self.create_socket()
        if self.is_unlimited_mode:
            border = float('+inf')
        else:
            border = self.count
        i = 0
        while i < border:
            self.send_packet()
            self.receive_data(self.interval)
            i += 1
        if self.timeout > self.interval:
            self.receive_data(self.timeout - self.interval)

    def receive_data(self, timeout):
        rest_timeout = timeout
        while True:
            t = time.perf_counter()
            s, _, _ = select.select([self.sock], [], [], rest_timeout)
            if s:
                t = time.perf_counter() - t
                rest_timeout = max(rest_timeout - t, 0)
                data = s[0].recvfrom(1024)
                self.parse_packet(data, time.perf_counter())
            else:
                break

    def get_statistics(self):
        self.stats.calculate()

    def print_primary_statistics(self):
        print()
        print('Packets sent: {}'.format(self.count_of_packets_sent))
        print('Packets received: {}'.format(self.count_of_received_packets))
        print('Packets loss: {}'.format(self.count_of_packets_sent - self.count_of_received_packets))

    def print_packet_statistics(self):
        print(self.stats)

    def process_data(self):
        self.print_primary_statistics()
        if self.count_of_received_packets > 0:
            self.get_statistics()
            self.print_packet_statistics()

    def signal_handler(self, a, b):
        self.process_data()

