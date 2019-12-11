import sys


class Visualiser:
    def sent_packet_info(self, packet):
        pass

    @staticmethod
    def sent_stat_info(p_stat, stat_mng):
        sent, received, loss = p_stat
        print()
        print(f'Packets sent: {sent}')
        print(f'Packets received: {received}')
        print(f'Packets loss: {loss}')
        print(stat_mng)


class StreamVisualiser(Visualiser):
    def __init__(self, timeout):
        self.timeout = timeout

    def sent_packet_info(self, packet):
        if packet.time > self.timeout:
            sys.stdout.write('_')
            sys.stdout.flush()
            return
        if packet.is_rst:
            sys.stdout.write('x')
            sys.stdout.flush()
            return
        sys.stdout.write('*')
        sys.stdout.flush()


class TimeVisualiser(Visualiser):
    def sent_packet_info(self, packet):
        print(packet.time)