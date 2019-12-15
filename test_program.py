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

    def recv_packets(self, timeout):
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
    def test_send_packets(self):
        address = (('1.1.1.1', 10), ('2.2.2.2', 20), ('3.3.3.3', 30))
        sock = FSocket([])
        program = Program.Program(0, address, (1, 1, 1), FStat(), FVisualiser, sock, FTimer(), False)
        program.send_packet()

        self.assertEqual(program.count_of_packets_sent, len(sock.send), 'Wrong count of send packets')