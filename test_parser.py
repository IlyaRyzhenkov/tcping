import Parser
import unittest


class TestParser(unittest.TestCase):
    def test_parse1(self):
        data = b"\x45\x00" \
            b"\x00\x29\x6f\x94\x40\x00\x80\x06\xe3\xd7\xc0\xa8\x00\x67\x40\xe9" \
            b"\xa5\x6a\xc6\x1b\x01\xbb\x78\x25\xc3\x2f\x0d\x8c\xb3\x0b\x50\x10" \
            b"\x01\x00\x43\xad\x00\x00\x00"
        packet = Parser.Parser(data)
        self.assertEqual('192.168.0.103', packet.source_ip, "Wrong source ip")
        self.assertEqual('64.233.165.106', packet.dest_ip, "Wrong destination ip")
        self.assertEqual(50715, packet.source_port, "Wrong source port")
        self.assertEqual(443, packet.dest_port, "Wrong destination port")
        self.assertEqual(2015740719, packet.seqence, "Wrong sequence number")
        self.assertEqual(227324683, packet.ack, "Wrong ack number")
        self.assertEqual(20496, packet.flags, "Wrong flag field value")
        self.assertTrue(packet.is_ack, "Wrong ACK flag value")
        self.assertFalse(packet.is_syn, "Wrong SYN flag value")
        self.assertFalse(packet.is_fin, "Wrong FIN flag value")
        self.assertFalse(packet.is_rst, "Wrong RST flag value")
        self.assertEqual(str(packet),
                         'Source ip:192.168.0.103\nDest ip:64.233.165.106\n'
                         'Source port:50715\nDest port:443\nSequence:2015740719\n'
                         'Acknowledge:227324683\nFlags:20496\nThis is Ack packet\n',
                         "Wrong string representation")

    def test_filter(self):
        packet1 = Parser.Parser(b'asdadsadadadadsasdasdasdasdadadsasdadasdadsasdasdasdasdasdad')
        packet1.source_ip = '1.1.1.1'
        packet2 = Parser.Parser(b'asdasdasdasdasdasdasdasdasdasdasdasdasdasdadsasdasdasdasdasd')
        packet2.source_ip = '2.2.2.2'

        addr_list = [('1.1.1.1', 50), ('1.2.3.4', 60)]
        self.assertTrue(packet1.filter_by_addr_list(addr_list), "Wrong filter for first ip")
        self.assertFalse(packet2.filter_by_addr_list(addr_list), "Wrong filter for second ip")
