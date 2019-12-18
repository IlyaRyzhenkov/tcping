import sys


class Visualiser:
    def sent_packet_info(self, packet, answer):
        pass

    @staticmethod
    def sent_stat_info(stat_mng):
        print()
        print(stat_mng.get_non_table_stat())
        print(stat_mng.get_table())


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
        packet_type = 'RST' if answer.is_rst else 'ACK'
        print(f'{packet.dest_ip}:{packet.dest_port} {round(packet.time, 3)} ({packet_type})')
