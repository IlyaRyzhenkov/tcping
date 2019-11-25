import itertools
import struct


class HeaderCreator:
    def __init__(self, source_ip, dest_ip, source_port, dest_port, seq_num):

        self.ip_version_length = b'\x45\x00\x00\x28'
        # version 4, IHL 5, type of service, Total length 40
        self.ip_fragmentation = b'\xab\xcd\x00\x00'
        self.ttl_tcp_protocol = b'\x40\x06'
        self.source_ip = self.parse_IP(source_ip)
        self.dest_ip = self.parse_IP(dest_ip)
        self.IP_checksum = self.get_IP_checksum()

        self.source_port = source_port.to_bytes(2, byteorder='big')
        self.dest_port = dest_port.to_bytes(2, byteorder='big')
        self.seq = seq_num.to_bytes(4, byteorder='big')
        self.ack = b'\x00\x00\x00\x00'
        self.TCP_header_len_flags = b'\x50\x02'
        # length 8 (32)bytes, SYN flag
        self.window_size = b'\x71\x10'
        # 64240
        self.urgent_pointer = b'\x00\x00'
        self.TCP_checksum = self.get_TCP_checksum()
        # self.options = b'\x02\x04\x05\xb4\x01\x03\x03\x08\x01\x01\x04\x02'
        self.options = b''

        self.send_time = 0
        self.answer_time = 0
        self.is_answered = False
        self.time = -1

    @staticmethod
    def get_pairs(it):
        prev = None
        for i in it:
            if prev is not None:
                yield prev * 256 + i
                prev = None
            else:
                prev = i

    def get_IP_checksum(self):
        presum = sum(self.get_pairs(
            itertools.chain(self.ip_version_length, self.ip_fragmentation,
                            self.ttl_tcp_protocol, self.source_ip,
                            self.dest_ip)))

        if presum // 65536 > 0:
            div = presum // 65536
            presum = presum % 65536 + div
        return (65535 - presum).to_bytes(2, byteorder='big')

    def get_TCP_checksum(self):
        presum = sum(self.get_pairs(
            itertools.chain(b'\x00\x06', self.source_ip, self.dest_ip,
                            b'\x00\x14', self.source_port,
                            self.dest_port, self.seq, self.ack,
                            self.TCP_header_len_flags, self.window_size)))
        if presum // 65536 > 0:
            div = presum // 65536
            presum = presum % 65536 + div
        return (65535 - presum).to_bytes(2, byteorder='big')

    @staticmethod
    def parse_IP(ip):
        numbers = map(int, ip.split('.'))
        return struct.pack('BBBB', *numbers)

    def make_SYN_query(self):
        IP_header = b''.join(
            [self.ip_version_length, self.ip_fragmentation, self.ttl_tcp_protocol,
             self.IP_checksum, self.source_ip, self.dest_ip])
        TCP_header = b''.join([
            self.source_port, self.dest_port, self.seq, self.ack, self.TCP_header_len_flags,
            self.window_size, self.TCP_checksum, self.urgent_pointer
        ])
        return IP_header + TCP_header
