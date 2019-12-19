import unittest
from resources import Program, Visualiser
from tests import test_statistic
import copy


class FakeSocket:
    def __init__(self, packets_to_recv, is_created=True, timer=None):
        self.send = []
        self.packets_to_recv = packets_to_recv
        self.ind = 0
        self.is_created = is_created
        self.is_closed = False
        self.timer = timer

    @staticmethod
    def get_host():
        return '0.0.0.0'

    def create(self, source_ip, source_port):
        self.is_created = True

    def send_packet(self, data, address):
        if self.is_closed or not self.is_created:
            raise RuntimeError
        self.send.append((address, data))

    def recv_data(self, timeout):
        if self.is_closed or not self.is_created:
            raise RuntimeError
        if self.ind >= len(self.packets_to_recv):
            return None
        if self.packets_to_recv[self.ind][0] < timeout:
            if self.timer:
                self.timer.increase(self.packets_to_recv[self.ind][0])
            data = self.packets_to_recv[self.ind][1]
            self.ind += 1
            return data
        self.ind += 1
        if self.timer:
            self.timer.increase(timeout)
        return None

    def close(self):
        self.is_closed = True


class FakeTimer:
    def __init__(self):
        self.time = 0

    def get_time(self):
        self.time += 1
        return self.time

    def increase(self, num):
        self.time += num


class FakeVisualiser(Visualiser.Visualiser):
    @staticmethod
    def sent_stat_info(p_stat, stat_mng):
        pass


class FakeStat:
    def add_address(self, address):
        pass

    def add_stat(self, stat):
        pass

    def update_on_sent(self, addr, packet):
        pass

    def update_on_receive(self, addr, packet):
        pass

    def calculate(self):
        pass


class TestProgram(unittest.TestCase):
    ADDRESS = (('1.1.1.1', 10), ('2.2.2.2', 20), ('3.3.3.3', 30))
    VALID_PACKET = b"\x45\x00\x00\x2c\x00\x00\x40\x00\x36\x06\x0b" \
                   b"\xf3\xd4\xc1\xa3\x07\xc0\xa8\x00\x68\x00\x50" \
                   b"\x00\x00\xee\x94\xcf\x8f\x00\x00\x00\x0b\x60" \
                   b"\x12\x72\x10\x2e\xe9\x00\x00\x02\x04\x05\x78" \
                   b"\x00\x00"

    def test_send_packets(self):
        sock = FakeSocket([])
        program = Program.Program(
            0, self.ADDRESS, (1, 1, 1), FakeStat(),
            FakeVisualiser(), sock, FakeTimer(), False)
        program.send_packet()

        self.assertEqual(
            program.count_of_packets_sent, len(sock.send),
            'Wrong count of send packets')
        for i in range(3):
            self.assertEqual(
                sock.send[i][0], self.ADDRESS[i], 'Wrong address')
            self.assertIn(
                (i + 1) * 10, program.packets, 'Wrong packets storage')
            self.assertEqual(
                program.packets[(i + 1) * 10].send_time, i + 1,
                'Wrong send time')
        self.assertEqual(program.seq, 40, 'Wrong seq number')

    def test_receive_data_1packet(self):
        packets = ((1, (b'asdsasdasdasdasdasadsasdad', )),
                   (20, (b'asdasdasdasdasdasdasdadasdasdasadsad', )))
        sock = FakeSocket(packets)
        timer = FakeTimer()
        program = Program.Program(
            0, self.ADDRESS, (1, 5, 5), FakeStat(),
            FakeVisualiser(), sock, timer, False)
        program.receive_data(5)
        self.assertEqual(timer.time, 3)

    def test_no_received_packets(self):
        packets = ((20, (b'asdasdasdasdasdasdasdadasdasdasadsad',)),)
        sock = FakeSocket(packets)
        timer = FakeTimer()
        program = Program.Program(
            0, self.ADDRESS, (1, 5, 5), FakeStat(),
            FakeVisualiser(), sock, timer, False)
        program.receive_data(5)
        self.assertEqual(timer.time, 1)

    def test_receive_multiple_packets(self):
        packets = ((1, (b'asdsasdasdasdasdasadsasdad',)),
                   (1, (b'asdasdasdasdasdasdasdadasdasdasadsad',)),
                   (1, (b'asdsasdasdasdasdasadsasdad',)),
                   (20, (b'asdsasdasdasdasdasadsasdad',)))
        sock = FakeSocket(packets)
        timer = FakeTimer()
        program = Program.Program(
            0, self.ADDRESS, (1, 5, 5), FakeStat(),
            FakeVisualiser(), sock, timer, False)
        program.receive_data(5)
        self.assertEqual(timer.time, 3)

    def test_parse_valid_packet(self):
        address = (('212.193.163.7', 80),)
        program = Program.Program(
            0, address, (1, 3, 3), FakeStat(), FakeVisualiser(),
            FakeSocket([]), FakeTimer(), False)
        program.packets[10] = test_statistic.FPacket(0)
        program.parse_packet((self.VALID_PACKET, ('212.193.163.7', 80)), 2)
        self.assertTrue(program.packets[10].is_answered,
                        'Wrong is_answered flag value')
        self.assertEqual(program.packets[10].time, 2,
                         'Wrong packet time')
        self.assertEqual(program.count_of_received_packets, 1,
                         'Wrong count of received packets')

    def test_parse_two_valid_packets(self):
        address = (('212.193.163.7', 80),)
        program = Program.Program(
            0, address, (1, 3, 3), FakeStat(), FakeVisualiser(),
            FakeSocket([]), FakeTimer(), False)
        program.packets[10] = test_statistic.FPacket(0)
        program.parse_packet((self.VALID_PACKET,
                              ('212.193.163.7', 80)), 2)
        program.parse_packet((self.VALID_PACKET,
                              ('212.193.163.7', 80)), 10)
        self.assertTrue(program.packets[10].is_answered,
                        'Wrong is_answered flag value')
        self.assertEqual(program.packets[10].time, 2,
                         'Wrong packet time')
        self.assertEqual(program.count_of_received_packets, 1,
                         'Wrong count of received packets')

    def test_parse_non_tcp(self):
        address = (('212.193.163.7', 80),)
        program = Program.Program(
            0, address, (1, 3, 3), FakeStat(), FakeVisualiser(),
            FakeSocket([]), FakeTimer(), False)
        program.packets[10] = test_statistic.FPacket(0)
        val1 = copy.deepcopy(program.packets)
        program.parse_packet(
            (b'asdasdadsasdasdasdasdasdasdasdasdasdasdasdasdasd',
             ('212.193.163.7', 80)), 0)
        val2 = program.packets
        self.assertDictEqual(val1, val2,
                             'Invalid packet don\'t sorted')

    def test_parse_bad_addr_packet(self):
        packet = b"\x45\x00\x00\x2c\x00\x00\x40\x00\x36\x06\x0b" \
                 b"\xf3\xa4\xa1\xa0\xa7\xc0\xa8\x00\x68\x00\x50" \
                 b"\x00\x00\xee\x94\xcf\x8f\x00\x00\x00\x0b\x60" \
                 b"\x12\x72\x10\x2e\xe9\x00\x00\x02\x04\x05\x78" \
                 b"\x00\x00"
        address = (('212.193.163.7', 80),)
        program = Program.Program(
            0, address, (1, 3, 3), FakeStat(), FakeVisualiser(),
            FakeSocket([]), FakeTimer(), False)
        program.packets[10] = test_statistic.FPacket(0)
        val1 = copy.deepcopy(program.packets)
        program.parse_packet((packet, ('212.193.163.7', 80)), 0)
        val2 = program.packets
        self.assertDictEqual(val1, val2,
                             'Invalid packet don\'t sorted')

    def test_parse_bad_ack_packet(self):
        packet = b"\x45\x00\x00\x2c\x00\x00\x40\x00\x36\x06\x0b" \
                 b"\xf3\xd4\xc1\xa3\x07\xc0\xa8\x00\x68\x00\x50" \
                 b"\x00\x00\xee\x94\xcf\x8f\x00\x00\x0a\x0b\x60" \
                 b"\x12\x72\x10\x2e\xe9\x00\x00\x02\x04\x05\x78" \
                 b"\x00\x00"
        address = (('212.193.163.7', 80),)
        program = Program.Program(
            0, address, (1, 3, 3), FakeStat(), FakeVisualiser(),
            FakeSocket([]), FakeTimer(), False)
        program.packets[10] = test_statistic.FPacket(0)
        val1 = copy.deepcopy(program.packets)
        program.parse_packet((packet, ('212.193.163.7', 80)), 0)
        val2 = program.packets
        self.assertDictEqual(val1, val2,
                             'Invalid packet don\'t sorted')

    def test_parse_timeout_packet(self):
        address = (('212.193.163.7', 80),)
        program = Program.Program(
            0, address, (1, 3, 3), FakeStat(), FakeVisualiser(),
            FakeSocket([]), FakeTimer(), False)
        program.packets[10] = test_statistic.FPacket(0)
        program.parse_packet((self.VALID_PACKET,
                              ('212.193.163.7', 80)), 10)
        self.assertTrue(program.packets[10].is_answered)
        self.assertEqual(program.packets[10].time, 10)
        self.assertEqual(program.count_of_received_packets, 0)

    def test_send_recv_packet(self):
        address = (('212.193.163.7', 80),)
        packets = ((1, (self.VALID_PACKET,)),)
        sock = FakeSocket(packets, False)
        program = Program.Program(
            0, address, (1, 10, 2), FakeStat(),
            FakeVisualiser(), sock, FakeTimer(), False)
        program.send_and_receive_packets()
        self.assertEqual(len(sock.send), 1,
                         'Wrong count of send packets')
        self.assertEqual(program.count_of_packets_sent, 1,
                         'Wrong packet_send value')
        self.assertEqual(program.count_of_received_packets, 1,
                         'Wrong packet_received value')
        self.assertTrue(sock.is_created, 'Socket is not created')
        self.assertTrue(sock.is_closed, 'Socket is not closed')
