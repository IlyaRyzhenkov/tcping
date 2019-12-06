import socket
import argparse
import Program
import sys
import Statistics


def parse_args():
    arg_parser = argparse.ArgumentParser(description='TCPing console app')
    arg_parser.add_argument('dest_ip', metavar='dest_ip',
                            help='Destination ip address')
    arg_parser.add_argument('dest_port', metavar='dest_port',
                            type=check_non_negative_int, help='Destination port address')
    arg_parser.add_argument('-t', '--timeout', type=check_non_negative_float, default=3,
                            help='Timeout for waiting packets')
    arg_parser.add_argument('-p', '--packet', type=check_non_negative_int, default=3,
                            help='Count of packets')
    arg_parser.add_argument('-i', '--interval', type=check_non_negative_float, default=1,
                            help='Packet sending interval')
    res = arg_parser.parse_args()
    if sys.platform == 'win32':
        print('Windows don\'t supported')
        sys.exit(0)
    if res.timeout <= 0:
        sys.stderr.write('Timeout should be positive')
        sys.exit(1)
    if res.packet <= 0:
        sys.stderr.write('Packet count should be positive')
        sys.exit(2)
    if res.interval < 0:
        sys.stderr.write('Interval should not be negative')
        sys.exit(3)
    try:
        ip = socket.gethostbyname(res.dest_ip)
    except socket.gaierror:
        sys.stderr.write('Incorrect destination address')
        sys.exit(4)
    return ip, res.dest_port, res.packet, res.timeout, res.interval


def check_non_negative_int(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def check_non_negative_float(value):
    fvalue = float(value)
    if fvalue < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return fvalue


if __name__ == "__main__":
    source_ip = '0.0.0.0'
    source_port = 0
    dest_ip, dest_port, packet_count, timeout, interval = parse_args()
    min_stat = Statistics.MinTimeStat()
    max_stat = Statistics.MaxTimeStat()
    avg_stat = Statistics.AverageTimeStat()
    program = Program.Program(
        (source_ip, source_port),
        (dest_ip, dest_port),
        (packet_count, timeout, interval),
        (min_stat, max_stat, avg_stat))
    program.send_and_receive_packets()
    program.process_data()
    program.print_statistics()
