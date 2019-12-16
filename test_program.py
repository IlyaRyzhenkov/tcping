import unittest
import Program
import Visualiser


class FSocket:
    def __init__(self, packets_to_recv):
        self.send = []
        self.packets_to_recv = packets_to_recv
        self.ind = 0

    @staticmethod
    def get_host():
        return '0.0.0.0'

    def create(self):
        pass

    def send_packet(self, data, address):
        self.send.append((address, data))

    def recv_data(self, timeout):
        if self.packets_to_recv[self.ind][0] < timeout:
            data = self.packets_to_recv[self.ind][1]
            self.ind += 1
            return data
        self.ind += 1
        return None

    def close(self):
        pass


class FTimer:
    def __init__(self):
        self.time = 0

    def get_time(self):
        self.time += 1
        return self.time


class FVisualiser(Visualiser.Visualiser):
    @staticmethod
    def sent_stat_info(p_stat, stat_mng):
        pass


class FStat:
    def add_address(self, address):
        pass

    def add_stat(self, stat):
        pass

    def update(self, addr, packet):
        pass

    def calculate(self):
        pass


class TestProgram(unittest.TestCase):
    ADDRESS = (('1.1.1.1', 10), ('2.2.2.2', 20), ('3.3.3.3', 30))
    VALID_PACKET = b"\x00\x00\x00\x01\x00\x06\x10\xfe\xed\x6e\x20\x52\x00\x00\x08\x00" \
b"\x45\x00\x00\x2c\x00\x00\x40\x00\x36\x06\x0b\xf3\xd4\xc1\xa3\x07" \
b"\xc0\xa8\x00\x68\x00\x50\x00\x00\xee\x94\xcf\x8f\x00\x00\x00\x0b" \
b"\x60\x12\x72\x10\x2e\xe9\x00\x00\x02\x04\x05\x78\x00\x00"

    def test_send_packets(self):
        sock = FSocket([])
        program = Program.Program(0, self.ADDRESS, (1, 1, 1), FStat(), FVisualiser(), sock, FTimer(), False)
        program.send_packet()

        self.assertEqual(program.count_of_packets_sent, len(sock.send), 'Wrong count of send packets')
        for i in range(3):
            self.assertEqual(sock.send[i][0], self.ADDRESS[i], 'Wrong address')
            self.assertIn((i + 1) * 10, program.packets, 'Wrong packets storage')
            self.assertEqual(program.packets[(i + 1) * 10].send_time, i + 1, 'Wrong send time')
        self.assertEqual(program.seq, 40, 'Wrong seq number')

    def test_receive_data_1packet(self):
        packets = ((1, (b'asdsasdasdasdasdasadsasdad', )), (20, (b'asdasdasdasdasdasdasdadasdasdasadsad', )))
        sock = FSocket(packets)
        timer = FTimer()
        program = Program.Program(0, self.ADDRESS, (1, 5, 5), FStat(), FVisualiser(), sock, timer, False)
        program.receive_data(5)
        self.assertEqual(timer.time, 4)

    def test_no_received_packets(self):
        packets = ((20, (b'asdasdasdasdasdasdasdadasdasdasadsad',)),)
        sock = FSocket(packets)
        timer = FTimer()
        program = Program.Program(0, self.ADDRESS, (1, 5, 5), FStat(), FVisualiser(), sock, timer, False)
        program.receive_data(5)
        self.assertEqual(timer.time, 1)

    def test_receive_multiple_packets(self):
        packets = ((1, (b'asdsasdasdasdasdasadsasdad',)), (1, (b'asdasdasdasdasdasdasdadasdasdasadsad',)),
                   (1, (b'asdsasdasdasdasdasadsasdad',)), (20, (b'asdsasdasdasdasdasadsasdad',)))
        sock = FSocket(packets)
        timer = FTimer()
        program = Program.Program(0, self.ADDRESS, (1, 5, 5), FStat(), FVisualiser(), sock, timer, False)
        program.receive_data(5)
        self.assertEqual(timer.time, 10)
