import struct


class TCPPacketParser:
    def __init__(self, data):
        self.parse_data(data)

    def parse_data(self, data):
        self.segment_len = struct.unpack('>H', data[2:4])[0]
        self.proto = data[9]
        self.source_ip = "{}.{}.{}.{}".format(*data[12:16])
        self.dest_ip = "{}.{}.{}.{}".format(*data[16:20])
        if self.proto != 6:
            return
        (self.source_port, self.dest_port,
         self.seqence, self.ack,
         self.flags) = struct.unpack('>HHIIH', data[20:34])
        self.is_fin = self.flags & 1 == 1
        self.is_syn = self.flags & 2 == 2
        self.is_ack = self.flags & 16 == 16
        self.is_rst = self.flags & 4 == 4

    def __str__(self):
        message = \
            "Source ip:{s_ip}\nDest ip:{d_ip}\nSource port:{s_port}\n" \
            "Dest port:{d_port}\nSequence:{seq}" \
            "\nAcknowledge:{ack}\nFlags:{flags}\n".format(
                s_ip=self.source_ip, d_ip=self.dest_ip,
                s_port=self.source_port,
                d_port=self.dest_port, seq=self.seqence, ack=self.ack,
                flags=self.flags
            )
        if self.is_ack:
            message += "This is Ack packet\n"
        if self.is_fin:
            message += "This is Fin packet\n"
        return message

    def filter_by_addr_list(self, addr_list):
        for (addr, _) in addr_list:
            if self.source_ip == addr:
                return True
        return False
