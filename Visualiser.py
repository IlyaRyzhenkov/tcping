import sys


class Visualiser:
    def sent_packet_info(self, packet, answer):
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

    def sent_packet_info(self, packet, answer):
        if packet.time > self.timeout:
            sys.stdout.write('_')
        elif answer.is_rst:
            sys.stdout.write('x')
        else:
            sys.stdout.write('*')
        sys.stdout.flush()


class TimeVisualiser(Visualiser):
    def sent_packet_info(self, packet, answer):
        print(f'{packet.dest_ip}:{packet.dest_port} {round(packet.time, 3)}')
