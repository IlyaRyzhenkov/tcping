from resources import TCPPacketCreator


class AddressStatManager:
    def __init__(self, stats):
        self.address_stat = {}
        self.stats = list(stats)
        self.table_stats = []
        self.non_table_stats = []
        for stat in self.stats:
            if stat.IN_TABLE:
                self.table_stats.append(stat)
            else:
                self.non_table_stats.append(stat)

    def add_address(self, address):
        self.address_stat[address] = StatManager()
        for stat in self.stats:
            self.address_stat[address].add_statistics(stat())

    def add_stat(self, stat):
        if not issubclass(stat, Stat):
            raise ValueError
        self.stats.append(stat)
        if stat.IN_TABLE:
            self.stats.append(stat)
        for address in self.address_stat.values():
            address.add_statistics(stat())

    def update_on_receive(self, addr, packet):
        self.address_stat[addr].update_on_receive(packet)

    def update_on_sent(self, addr, packet):
        self.address_stat[addr].update_on_sent(packet)

    def calculate(self):
        for address in self.address_stat.values():
            address.calculate()

    def get_values(self):
        return [(address, stat) for address, stat in self.address_stat.items()]

    def __str__(self):
        return '\n'.join(f'{address[0]}:{address[1]}\n{stat}'
                         for address, stat in self.address_stat.items())

    def get_table(self):
        stats = [stat.NAME for stat in self.table_stats]
        table = '      IP       |PORT |' + '|'.join(stats) + '|\n'
        max_ip = max(map(len, (addr[0] for addr in self.address_stat.keys())))
        for addr, mng in self.address_stat.items():
            row = ('{ip:^15}:{port:^5}|'.format(ip=addr[0], port=addr[1]) +
                   ''.join(stat.get_format_data() for stat in mng.table_stats) + '\n')
            table += row
        return table

    def get_non_table_stats(self):
        return '\n'.join(f'{address[0]}:{address[1]}\n{stat.get_non_table_stats()}'
                         for address, stat in self.address_stat.items())


class StatManager:
    def __init__(self):
        self.stats = []
        self.non_table_stats = []
        self.table_stats = []

    def add_statistics(self, stat):
        self.stats.append(stat)
        if stat.IN_TABLE:
            self.table_stats.append(stat)
        else:
            self.non_table_stats.append(stat)

    def update_on_receive(self, packet):
        for stat in self.stats:
            stat.update_on_receive(packet)

    def update_on_sent(self, packet):
        for stat in self.stats:
            stat.update_on_sent(packet)

    def calculate(self):
        for stat in self.stats:
            stat.calculate()

    def get_values(self):
        return [stat.get_value() for stat in self.stats]

    def get_non_table_stats(self):
        return '\n'.join(map(str, self.non_table_stats))

    def __str__(self):
        return '\n'.join(map(str, self.stats))


class Stat:
    NAME = 'Stat'
    IN_TABLE = True

    def update_on_receive(self, packet):
        pass

    def update_on_sent(self, packet):
        pass

    def calculate(self):
        pass

    def get_value(self):
        pass

    def get_format_data(self):
        pass


class MaxTimeStat(Stat):
    NAME = 'Max time'

    def __init__(self):
        self.max = float('-inf')

    def update_on_receive(self, packet):
        if packet.time > self.max:
            self.max = packet.time

    def get_value(self):
        return self.max

    def calculate(self):
        self.max = round(self.max, 3)

    def __str__(self):
        if self.max != float('-inf'):
            return 'Max time: {}'.format(self.max)
        return 'Max time: Not calculated'

    def get_format_data(self):
        if self.max != float('-inf'):
            return '{max:^8}|'.format(max=self.max)
        return 'no data |'


class MinTimeStat(Stat):
    NAME = 'Min time'

    def __init__(self):
        self.min = float('+inf')

    def update_on_receive(self, packet):
        if packet.time < self.min:
            self.min = packet.time

    def get_value(self):
        return self.min

    def calculate(self):
        self.min = round(self.min, 3)

    def __str__(self):
        if self.min != float('+inf'):
            return 'Min time: {}'.format(self.min)
        return 'Min time: Not calculated'

    def get_format_data(self):
        if self.min != float('+inf'):
            return '{min:^8}|'.format(min=self.min)
        return 'no data |'


class AverageTimeStat(Stat):
    NAME = 'Average time'

    def __init__(self):
        self.sum = 0
        self.count = 0
        self.result = 0
        self.is_calculated = False

    def update_on_receive(self, packet):
        self.sum += packet.time
        self.count += 1
        self.is_calculaded = False

    def calculate(self):
        if self.count > 0:
            self.result = round(self.sum / self.count, 3)
            self.is_calculated = True

    def get_value(self):
        return self.result

    def __str__(self):
        if self.is_calculated:
            return 'Average time: {}'.format(self.result)
        return 'Average time: Not calculated'

    def get_format_data(self):
        if self.is_calculated:
            return '{avg:^12}|'.format(avg=self.result)
        return '  no data   |'


class PacketStatusStat(Stat):
    NAME = 'Packet status'
    IN_TABLE = False

    def __init__(self):
        self.send = 0
        self.receive = 0
        self.loss = 0
        self.rst = 0
        self.is_calculated = False

    def update_on_receive(self, packet):
        self.receive += 1
        if packet.answer_type == TCPPacketCreator.TcpPacketType.RST:
            self.rst += 1

    def update_on_sent(self, packet):
        self.send += 1

    def calculate(self):
        self.is_calculated = True
        self.loss = self.send - self.receive
        self.percent_receive = round((self.receive / self.send) * 100)
        self.percent_loss = round((self.loss / self.send) * 100)

    def get_value(self):
        return self.send, self.receive, self.loss, self.rst, self.percent_receive, self.percent_loss

    def __str__(self):
        if self.is_calculated:
            return f'Packet send: {self.send}\n' \
                   f'Packet received: {self.receive}, {self.percent_receive}% ({self.rst} RST)\n' \
                   f'Packet loss: {self.loss}, {self.percent_loss}%'
