import socket
import time
import select
import Creator
import sys
import Parcer
import Statistics


class Program:
    def __init__(self, source_addr, dest_addr, params, stats):
        self.source_ip, self.source_port = source_addr
        self.dest_ip, self.dest_port = dest_addr
        self.count, self.timeout, self.interval = params

        self.packets = {}
        self.answered_packets = []
        self.count_of_packets_sent = 0
        self.count_of_received_packets = 0
        self.packets_loss = 0

        self.stats = Statistics.StatManager()
        for stat in stats:
            self.stats.add_statistics(stat)

    def create_socket(self):
        tcp = socket.getprotobyname("tcp")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, tcp)
        self.sock.bind((self.source_ip, self.source_port))
        if sys.platform != 'win32':
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    def send_packet(self, seq):
        packet = Creator.HeaderCreator(
            self.source_ip, self.dest_ip,
            self.source_port, self.dest_port, seq)
        self.packets[seq] = packet
        self.sock.sendto(packet.make_SYN_query(),
                         (self.dest_ip, self.dest_port))
        t = time.perf_counter()
        packet.send_time = t
        self.count_of_packets_sent += 1
        sys.stdout.write('.')
        sys.stdout.flush()

    def parse_packet(self, data, recv_time):
        parser = Parcer.Parser(data[0])
        if parser.proto != 6:
            return
        if parser.filter_by_source_ip(self.dest_ip):
            seq = parser.ack - 1
            if seq in self.packets.keys():
                self.packets[seq].is_answered = True
                self.packets[seq].answer_time = recv_time
                self.packets[seq].time = recv_time - \
                                         self.packets[seq].send_time
                if self.packets[seq].time < self.timeout:
                    self.count_of_received_packets += 1
                    sys.stdout.write('*')
                    sys.stdout.flush()
                else:
                    self.packets_loss += 1
                    sys.stdout.write('_')
                    sys.stdout.flush()

    def send_and_receive_packets(self):
        self.create_socket()
        for i in range(self.count):
            self.send_packet((i + 1) * 10)
            self.receive_data(self.interval)
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

    def filter_loss_packets(self):
        for seq in self.packets:
            packet = self.packets[seq]
            if not packet.is_answered:
                self.packets_loss += 1
            else:
                self.answered_packets.append(packet)

    def get_statistics(self):
        self.stats.calculate(self.answered_packets)

    def print_statistics(self):
        print()
        print('Packets sent: {}'.format(self.count_of_packets_sent))
        print('Packets received: {}'.format(self.count_of_received_packets))
        print('Packets loss: {}'.format(self.packets_loss))
        print(self.stats)

    def process_data(self):
        self.filter_loss_packets()
        if self.count_of_received_packets > 0:
            self.get_statistics()
