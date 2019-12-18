class AddressStatManager:
    def __init__(self, stats):
        self.address_stat = {}
        self.stats = list(stats)

    def add_address(self, address):
        self.address_stat[address] = StatManager()
        for stat in self.stats:
            self.address_stat[address].add_statistics(stat())

    def add_stat(self, stat):
        if not issubclass(stat, Stat):
            raise ValueError
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
        self.get_table()
        return '\n'.join(f'{address[0]}:{address[1]}\n{stat}' for address, stat in self.address_stat.items())

    def get_table(self):
        stats = [stat.NAME for stat in self.stats]
        print(stats)

class StatManager:
    def __init__(self):
        self.stats = []

    def add_statistics(self, stat):
        self.stats.append(stat)

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

    def __str__(self):
        return '\n'.join(map(str, self.stats))


class Stat:
    NAME = 'Stat'

    def update_on_receive(self, packet):
        pass

    def update_on_sent(self, packet):
        pass

    def calculate(self):
        pass

    def get_value(self):
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


class AverageTimeStat(Stat):
    NAME = 'Average time'

    def __init__(self):
        self.sum = 0
        self.count = 0
        self.result = 0

    def update_on_receive(self, packet):
        self.sum += packet.time
        self.count += 1

    def calculate(self):
        if self.count > 0:
            self.result = round(self.sum / self.count, 3)

    def get_value(self):
        return self.result

    def __str__(self):
        if self.result:
            return 'Average time: {}'.format(self.result)
        return 'Average time: Not calculated'


class PacketStatusStat(Stat):
    NAME = 'Packe status'

    def __init__(self):
        self.send = 0
        self.receive = 0
        self.loss = 0
        self.is_calculated = False

    def update_on_receive(self, packet):
        self.receive += 1

    def update_on_sent(self, packet):
        self.send += 1

    def calculate(self):
        self.is_calculated = True
        self.loss = self.send - self.receive
        self.percent_receive = round((self.receive / self.send) * 100)
        self.percent_loss = round((self.loss / self.send) * 100)

    def get_value(self):
        return self.send, self.receive, self.loss, self.percent_receive, self.percent_loss

    def __str__(self):
        if self.is_calculated:
            return f'Packet send: {self.send}\n' \
                   f'Packet received: {self.receive}, {self.percent_receive}%\n' \
                   f'Packet loss: {self.loss}, {self.percent_loss}%'
