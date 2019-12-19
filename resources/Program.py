from resources import TCPPacketCreator, TCPPacketParser
import itertools


class Program:
    def __init__(self, source_port, address, params,
                 stats, visualiser, socket, timer, mode):
        self.sock = socket
        self.source_port = source_port
        self.source_ip = self.sock.get_host()
        self.address = address
        self.count, self.timeout, self.interval = params
        self.visualiser = visualiser
        self.timer = timer
        self.is_unlimited_mode = mode

        self.packets = {}
        self.count_of_packets_sent = 0
        self.count_of_received_packets = 0
        self.seq = 10

        self.stats = stats
        for addr in self.address:
            self.stats.add_address(addr)

    def create_socket(self):
        self.sock.create(self.source_ip, self.source_port)

    def close_socket(self):
        self.sock.close()

    def send_packet(self):
        for addr in self.address:
            packet = TCPPacketCreator.TCPPacketCreator(
                self.source_ip, addr[0],
                self.source_port, addr[1], self.seq)
            self.packets[self.seq] = packet
            self.sock.send_packet(packet.make_SYN_query(), addr)
            t = self.timer.get_time()
            packet.send_time = t
            # Запоминаю время отправки пакета
            self.count_of_packets_sent += 1
            self.seq += 10
            self.stats.update_on_sent(addr, packet)

    def parse_packet(self, data, recv_time):
        parser = TCPPacketParser.TCPPacketParser(data[0])
        if parser.proto != 6:
            return
        if parser.filter_by_addr_list(self.address):
            seq = parser.ack - 1
            if (seq in self.packets.keys() and not
                    self.packets[seq].is_answered):
                self.packets[seq].is_answered = True
                self.packets[seq].answer_type = (
                    TCPPacketCreator.TcpPacketType.RST if parser.is_rst else
                    TCPPacketCreator.TcpPacketType.ACK)
                self.packets[seq].answer_time = recv_time
                self.packets[seq].time = recv_time - \
                    self.packets[seq].send_time
                # расчитывается время ответа
                if self.packets[seq].time < self.timeout:
                    self.count_of_received_packets += 1
                    self.stats.update_on_receive(
                        (parser.source_ip, parser.source_port),
                        self.packets[seq])
                    self.visualiser.sent_packet_info(self.packets[seq], parser)

    def send_and_receive_packets(self):
        self.create_socket()
        if self.is_unlimited_mode:
            border = float('+inf')
        else:
            border = self.count
        for i in (itertools.count() if self.is_unlimited_mode else
                  range(self.count)):
            self.send_packet()
            self.receive_data(self.interval)
            i += 1
        if (self.timeout > self.interval and
                self.count_of_received_packets < border):
            self.receive_data(self.timeout - self.interval)
        self.sock.close()

    def receive_data(self, timeout):
        rest_timeout = timeout
        while True:
            t = self.timer.get_time()
            data = self.sock.recv_data(rest_timeout)
            if not data:
                break
            t = self.timer.get_time() - t
            rest_timeout = max(rest_timeout - t, 0)
            # вызывается парсер с временем приема ответа
            self.parse_packet(data, self.timer.get_time())
            if self.count_of_packets_sent == self.count_of_received_packets:
                break

    def process_data(self):
        self.stats.calculate()
        self.visualiser.sent_stat_info(self.stats)

    def signal_handler(self, a, b):
        self.process_data()

    @staticmethod
    def inf_range(num):
        i = 0
        while i < num:
            yield i
            i += 1
