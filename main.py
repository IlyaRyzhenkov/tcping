import socket
import sys
import Creator
import Parcer
import argparse


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
    return ip, res.dest_port, res.timeout, res.packet, res.interval


def receive_data(sock, ip):
    data = s.recvfrom(2048)
    print("Data received:")
    parser = Parcer.Parser(data[0])
    print(parser, ip)
    if parser.filter_by_source_ip(ip):
        return True
    return False


if __name__ == "__main__":
    source_ip = '0.0.0.0'
    source_port = 0
    dest_ip, dest_port, timeout, packet_count, interval = parse_args()
    creator = Creator.HeaderCreator(
        source_ip, dest_ip, source_port, dest_port, 0)
    packet = creator.make_SYN_quarry()
    if sys.platform == 'win32':
        tcp = socket.IPPROTO_IP
    else:
        tcp = socket.getprotobyname("tcp")
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, tcp)
    s.bind((source_ip, source_port))
    #s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    s.sendto(packet, (dest_ip, dest_port))
    print("Sending to ({}, {})".format(dest_ip, dest_port))

    while True:
        if receive_data(s, dest_ip):
            break
