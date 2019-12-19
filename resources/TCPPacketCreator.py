import itertools
import struct
import enum


class HeaderCreator:
    IP_VERSION_LENGHT = b'\x45\x00\x00\x28'
    # version 4, IHL 5, type of service, Total length 40
    IP_FRAGMENTATION = b'\xab\xcd\x00\x00'
    TTL_TCP_PROTOCOL = b'\x40\x06'
    CONST_IP_CHECKSUM = 78075

    ACK = b'\x00\x00\x00\x00'
    TCP_HEADER_LEN_FLAGS = b'\x50\x02'
    # length 8 (32)bytes, SYN flag
    WINDOW_SIZE = b'\x71\x10'
    # 64240
    URGENT_POINTER = b'\x00\x00'
    CONST_TCP_CHECKSUM = 49426

    def __init__(self, source_ip, dest_ip, source_port, dest_port, seq_num):
        self.source_ip = self.parse_IP(source_ip)
        self.dest_ip = self.parse_IP(dest_ip)
        self.IP_checksum = self.get_IP_checksum()

        self.source_port = source_port.to_bytes(2, byteorder='big')
        self.dest_port = dest_port.to_bytes(2, byteorder='big')
        self.seq = seq_num.to_bytes(4, byteorder='big')
        self.TCP_checksum = self.get_TCP_checksum()

        self.answer_type = None
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
            itertools.chain(self.source_ip, self.dest_ip))) + self.CONST_IP_CHECKSUM

        if presum >> 16 > 0:
            div = presum >> 16
            presum = (presum & 65535) + div
        return (65535 - presum).to_bytes(2, byteorder='big')

    def get_TCP_checksum(self):
        presum = sum(self.get_pairs(
            itertools.chain(b'\x00\x06', self.source_ip, self.dest_ip,
                            b'\x00\x14', self.source_port,
                            self.dest_port, self.seq))) + self.CONST_TCP_CHECKSUM
        if presum >> 16 > 0:
            div = presum >> 16
            presum = (presum & 65535) + div
        return (65535 - presum).to_bytes(2, byteorder='big')

    @staticmethod
    def parse_IP(ip):
        numbers = map(int, ip.split('.'))
        return struct.pack('BBBB', *numbers)

    def make_SYN_query(self):
        IP_header = b''.join(
            [self.IP_VERSION_LENGHT, self.IP_FRAGMENTATION, self.TTL_TCP_PROTOCOL,
             self.IP_checksum, self.source_ip, self.dest_ip])
        TCP_header = b''.join([
            self.source_port, self.dest_port, self.seq, self.ACK, self.TCP_HEADER_LEN_FLAGS,
            self.WINDOW_SIZE, self.TCP_checksum, self.URGENT_POINTER
        ])
        return IP_header + TCP_header


class TcpPacketType(enum.Enum):
    RST = 0
    ACK = 1
