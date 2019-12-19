import unittest
from resources import TCPPacketCreator


class TestCreator(unittest.TestCase):
    def test_parse_ip(self):
        expected = b'\x01\x02\x03\x04'
        actual = TCPPacketCreator.HeaderCreator.parse_IP('1.2.3.4')
        self.assertEqual(
            expected, actual,
            "Wrong parsed ip\nexp: {}\nact: {}".format(expected, actual))

    def test_get_ip_checksum(self):
        expected = b'\xa6\xec'
        creator = TCPPacketCreator.HeaderCreator(
            '10.10.10.2', '10.10.10.1', 12345, 80, 0)
        actual = creator.get_IP_checksum()
        self.assertEqual(
            expected, actual,
            "Wrong ip checksum\nexp: {}\nack: {}".format(expected, actual))

    def test_get_tcp_checksum(self):
        expected = b'\xe6\x32'
        creator = TCPPacketCreator.HeaderCreator(
            '10.10.10.2', '10.10.10.1', 12345, 80, 0)
        actual = creator.get_TCP_checksum()
        self.assertEqual(
            expected, actual,
            "Wrong TCP checksum\nexp: {}\nact: {}".format(expected, actual))

    def test_create_SYN_packet(self):
        expected = b'\x45\x00\x00\x28\xab\xcd\x00\x00\x40\x06\xa6'
        expected += b'\xec\x0a\x0a\x0a\x02\x0a\x0a\x0a\x01\x30\x39'
        expected += b'\x00\x50\x00\x00\x00\x00\x00\x00\x00\x00\x50'
        expected += b'\x02\x71\x10\xe6\x32\x00\x00'

        creator = TCPPacketCreator.HeaderCreator(
            '10.10.10.2', '10.10.10.1', 12345, 80, 0)
        packet = creator.make_SYN_query()

        self.assertEqual(
            expected, packet,
            "Wrong packet\nexp: {}\nwas: {}".format(expected, packet))
