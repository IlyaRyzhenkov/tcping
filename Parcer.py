class Parser:
    def __init__(self, data):
        self.parse_data(data)

    def parse_data(self, data):
        self.segment_len = int.from_bytes(data[2:4], byteorder="big")
        self.source_ip = "{}.{}.{}.{}".format(data[12], data[13],
                                              data[14], data[15])
        self.dest_ip = "{}.{}.{}.{}".format(data[16], data[17],
                                            data[18], data[19])
        self.source_port = int.from_bytes(data[20:22], byteorder="big")
        self.dest_port = int.from_bytes(data[22:24], byteorder="big")
        self.seqence = int.from_bytes(data[24:28], byteorder="big")
        self.ack = int.from_bytes(data[28:32], byteorder="big")
        self.flags = bin(int.from_bytes(data[32:34], byteorder="big"))
        try:
            self.is_ack = self.flags[-5] == '1'
            self.is_syn = self.flags[-2] == '1'
            self.is_fin = self.flags[-1] == '1'
        except IndexError:
            self.is_ack = False
            self.is_syn = False
            self.is_fin = self.flags == '0b1'

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

    def filter_by_source_ip(self, source_ip):
        return self.source_ip == source_ip
