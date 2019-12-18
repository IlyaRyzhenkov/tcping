import sys


class Visualiser:
    def sent_packet_info(self, packet, answer):
        pass

    @staticmethod
    def sent_stat_info(stat_mng):
        print()
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
