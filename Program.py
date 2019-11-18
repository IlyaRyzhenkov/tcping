import socket
import time
import select
import Creator
import sys
import Parcer


class Programm:
    def __init__(self, source_addr, dest_addr, params):
        self.source_ip, self.source_port = source_addr
        self.dest_ip, self.dest_port = dest_addr
        self.count, self.timeout, self.interval = params

        self.packets = {}
        self.answered_packets = []
        self.count_of_packets_sent = 0
        self.count_of_received_packets = 0
        self.packets_loss = 0

        self.max_time = 0
        self.min_time = 0
        self.avg_time = 0

    def create_socket(self):
        if sys.platform == 'win32':
            tcp = socket.IPPROTO_IP
        else:
            tcp = socket.getprotobyname("tcp")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, tcp)
        self.sock.bind((self.source_ip, self.source_port))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    def send_packet(self, seq):
        packet = Creator.HeaderCreator(
            self.source_ip, self.dest_ip, self.source_port, self.dest_port, seq)
        self.packets[seq] = packet
        self.sock.sendto(packet.make_SYN_quarry(), (self.dest_ip, self.dest_port))
        t = time.perf_counter()
        packet.send_time = t
        self.count_of_packets_sent += 1
        print('.', end='')

    def parse_packet(self, data, recv_time):
        parser = Parcer.Parser(data[0])
        if parser.filter_by_source_ip(self.dest_ip):
            seq = parser.ack - 1
            if self.packets[seq]:
                self.packets[seq].is_answered = True
                self.packets[seq].answer_time = recv_time
                self.count_of_received_packets += 1
                print('*', end='')

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
                rest_timeout = rest_timeout - t
                data = s[0].recv(2048)
                self.parse_packet(data, time.perf_counter())
            else:
                break

    def filter_loss_packets(self):
        for seq in self.packets:
            packet = self.packets[seq]
            if not packet.is_answered:
                self.packets_loss += 1
                continue
            packet.time = packet.answer_time - packet.send_time
            if packet.time > self.timeout:
                self.packets_loss += 1
            else:
                self.answered_packets.append(packet)

    def get_statistics(self):
        min_time = float('+inf')
        max_time = 0
        total_time = 0
        for packet in self.answered_packets:
            if packet.time < min_time:
                min_time = packet.time
            if packet.time > max_time:
                max_time = packet.time
            total_time += packet.time

        self.min_time = min_time
        self.max_time = max_time
        self.avg_time = total_time / len(self.answered_packets)

    def print_statistics(self):
        print('Packets sent: {}'.format(self.count_of_packets_sent))
        print('Packets received: {}'.format(self.count_of_received_packets))
        print('Packets loss: {}'.format(self.packets_loss))
        if self.count_of_received_packets > 0:
            print('Min time: {}'.format(self.min_time))
            print('Max time: {}'.format(self.max_time))
            print('Average time: {}'.format(self.avg_time))

    def process_data(self):
        self.filter_loss_packets()
        if self.count_of_received_packets > 0:
            self.get_statistics()
        self.print_statistics()
