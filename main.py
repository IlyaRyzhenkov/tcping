import socket
import Creator
import sys

if __name__ == "__main__":
    source_ip = socket.gethostbyname(socket.gethostname())
    source_ip = "10.10.10.2"
    source_port = int(sys.argv[1])
    dest_ip = sys.argv[2]
    dest_port = int(sys.argv[3])
    creator = Creator.HeaderCreator(source_ip, dest_ip, source_port, dest_port, 0)
    packet = creator.make_SYN_quarry()

    HOST = socket.gethostbyname(socket.gethostname())
    print(HOST)
    # create a raw socket and bind it to the public interface
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    s.bind((HOST, source_port))

    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    s.sendto(packet, (dest_ip, dest_port))
