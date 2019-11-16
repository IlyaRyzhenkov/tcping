import socket
import Creator
import Parcer
import argparse


def check_is_correct_ip(ip):
    try:
        count = 0
        for num in map(int, ip.split('.')):
            count += 1
            if 0 <= num <= 255:
                continue
            else:
                return False
        if count != 4:
            return False
        else:
            return True
    except ValueError:
        return False


def parse_args():
    arg_parser = argparse.ArgumentParser(description="TCPing console app")
    arg_parser.add_argument(
        'dest_ip', metavar='dest_ip', help='Destination ip address')
    arg_parser.add_argument('dest_port', metavar='dest_port',
                            type=int, help='Destination port address')
    res = arg_parser.parse_args()
    if not check_is_correct_ip(res.dest_ip):
        print('Incorrect ip address: {}'.format(res.dest_ip))
        exit(1)
    return res.dest_ip, res.dest_port


def receive_data(sock):
    data = s.recvfrom(1024)
    print("Data received:")
    parser = Parcer.Parser()
    parser.parse_data(data[0])
    print(parser)


if __name__ == "__main__":
    source_ip = socket.gethostbyname(socket.gethostname())
    source_port = 12345
    dest_ip, dest_port = parse_args()
    creator = Creator.HeaderCreator(
        source_ip, dest_ip, source_port, dest_port, 0)
    packet = creator.make_SYN_quarry()

    tcp = socket.getprotobyname("tcp")
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    s.bind((source_ip, source_port))

    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    s.sendto(packet, (dest_ip, dest_port))
    print("Sending to ({}, {})".format(dest_ip, dest_port))

    receive_data(s)
    s.close()
