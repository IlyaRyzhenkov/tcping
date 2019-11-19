import socket
import argparse
import Program


def parse_args():
    arg_parser = argparse.ArgumentParser(description='TCPing console app')
    arg_parser.add_argument('dest_ip', metavar='dest_ip',
                            help='Destination ip address')
    arg_parser.add_argument('dest_port', metavar='dest_port',
                            type=int, help='Destination port address')
    arg_parser.add_argument('-t', '--timeout', type=float, default=3,
                            help='Timeout for waiting packets')
    arg_parser.add_argument('-p', '--packet', type=int, default=3,
                            help='Count of packets')
    arg_parser.add_argument('-i', '--interval', type=float, default=1,
                            help='Packet sending interval')
    res = arg_parser.parse_args()
    if res.timeout <= 0:
        print('Timeout should be positive')
        exit(1)
    if res.packet <= 0:
        print('Packet count should be positive')
        exit(2)
    if res.interval < 0:
        print('Interval should not be negative')
        exit(3)
    try:
        ip = socket.gethostbyname(res.dest_ip)
    except socket.gaierror:
        print('Incorrect destination address')
        exit(4)
    return ip, res.dest_port, res.packet, res.timeout, res.interval


if __name__ == "__main__":
    source_ip = '0.0.0.0'
    source_port = 0
    dest_ip, dest_port, packet_count, timeout, interval = parse_args()
    program = Program.Program(
        (source_ip, source_port),
        (dest_ip, dest_port),
        (packet_count, timeout, interval))
    program.send_and_receive_packets()
    program.process_data()
