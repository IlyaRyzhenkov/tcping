import socket
import Creator
import sys

if __name__ == "__main__":
    source_ip = socket.gethostbyname(socket.gethostname())
    source_port = int(sys.argv[1])
    dest_ip = sys.argv[2]
    dest_port = int(sys.argv[3])
    creator = Creator.HeaderCreator(source_ip, dest_ip, source_port, dest_port, 0)
    packet = creator.make_SYN_quarry()
	
    tcp = socket.getprotobyname("tcp")
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, tcp)

    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    s.sendto(packet, (dest_ip, dest_port))
    data = s.recvfrom(1024)
    print(data)