import socket
import argparse
import Program
import sys
import Statistics
import signal
import Visualiser
import SocketAPI
import Timer


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
                            help='Property for unlimited count of pings. '
                                 'You can get statistics by SIGUSR1')
    arg_parser.add_argument('-a', '--add',metavar=('HOST', 'PORT'),
                            nargs=2, action='append', help='Add another address for ping')
    arg_parser.add_argument('-v', action='store_true', help='Shows time for every packet')
    arg_parser.add_argument('-P', '--source_port', type=check_port, default=0,
                            help='source port for sending packets (default is 0)')
    res = arg_parser.parse_args()
    address = parse_additional_address(res.add)
    address.append((res.dest_ip, res.dest_port))
    return res, address


def check_port(port):
    if not (0 <= int(port) <= 65535):
        raise argparse.ArgumentTypeError
    return int(port)


def check_ip(ip):
    return socket.gethostbyname(ip)


def check_non_negative_int(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return ivalue


def check_non_negative_float(value):
    fvalue = float(value)
    if fvalue < 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive float value")
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
            sys.stderr.write('Wrong additional address {}'.format(' '.join(address)))
    return parsed


def parse_address(address):
    ip, port = address
    ip = socket.gethostbyname(ip)
    port = int(port)
    if not (0 <= port <= 65535):
        raise ValueError
    return ip, port


if __name__ == "__main__":
    if sys.platform == 'win32':
        sys.stderr.write('Windows don\'t supported')
        sys.exit(1)

    parsed, address = parse_args()
    source_port = parsed.source_port
    if parsed.v:
        visualiser = Visualiser.TimeVisualiser()
    else:
        visualiser = Visualiser.StreamVisualiser(parsed.timeout)
    stats = Statistics.AddressStatManager((Statistics.PacketStatusStat,
        Statistics.MinTimeStat, Statistics.MaxTimeStat, Statistics.AverageTimeStat))
    sock = SocketAPI.SocketAPI()
    timer = Timer.Timer()
    program = Program.Program(
        source_port,
        address,
        (parsed.packet, parsed.timeout, parsed.interval),
        stats, visualiser, sock, timer,
        parsed.unlimited)
    if parsed.unlimited:
        signal.signal(signal.SIGUSR1, program.signal_handler)
    program.send_and_receive_packets()
    if not parsed.unlimited:
        program.process_data()
