import socket
import argparse
import Program
import sys
import Statistics
import signal


def parse_args():
    arg_parser = argparse.ArgumentParser(description='TCPing console app')
    arg_parser.add_argument('dest_ip', metavar='dest_ip', type=check_ip,
                            help='Destination ip address')
    arg_parser.add_argument('dest_port', metavar='dest_port',
                            type=check_non_negative_int, help='Destination port address')
    arg_parser.add_argument('-t', '--timeout', type=check_non_negative_float, default=3,
                            help='Timeout for waiting packets')
    arg_parser.add_argument('-p', '--packet', type=check_non_negative_int, default=3,
                            help='Count of packets')
    arg_parser.add_argument('-i', '--interval', type=check_non_negative_float, default=1,
                            help='Packet sending interval')
    arg_parser.add_argument('-u', '--unlimited', action='store_true',
                            help='Property for unlimited count of pings. You can get statistics by SIGUSR1')
    arg_parser.add_argument('-a', '--add', nargs=2, action='append', help='Add another address for ping')
    res = arg_parser.parse_args()
    address = parse_additional_address(res.add)
    address.append((res.dest_ip, res.dest_port))
    if sys.platform == 'win32':
        print('Windows don\'t supported')
        sys.exit(0)
    return address, res.packet, res.timeout, res.interval, res.unlimited


def check_ip(ip):
    return socket.gethostbyname(ip)


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


def parse_additional_address(address_list):
    parsed = []
    if not address_list:
        return parsed
    for address in address_list:
        try:
            ip, port = parse_address(address)
            parsed.append((ip, port))
        except Exception:
            print('Wrong additional address {}'.format(' '.join(address)))
    return parsed


def parse_address(address):
    ip, port = address
    ip = socket.gethostbyname(ip)
    port = int(port)
    if 65536 < port or port < 0:
        raise ValueError
    return ip, port


if __name__ == "__main__":
    source_ip = '0.0.0.0'
    source_port = 0
    address, packet_count, timeout, interval, is_unlimited_mode = parse_args()
    min_stat = Statistics.MinTimeStat()
    max_stat = Statistics.MaxTimeStat()
    avg_stat = Statistics.AverageTimeStat()
    program = Program.Program(
        (source_ip, source_port),
        address,
        (packet_count, timeout, interval),
        (min_stat, max_stat, avg_stat),
        is_unlimited_mode)
    if is_unlimited_mode:
        signal.signal(signal.SIGUSR1, program.signal_handler)
    program.send_and_receive_packets()
    if not is_unlimited_mode:
        program.process_data()
