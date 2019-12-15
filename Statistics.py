class AddressStatManager:
    def __init__(self, stats):
        self.address_stat = {}
        self.stats = stats

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

    def update(self, addr, packet):
        self.address_stat[addr].update(packet)

    def calculate(self):
        for address in self.address_stat.values():
            address.calculate()

    def get_values(self):
        return [(address, stat) for address, stat in self.address_stat.items()]

    def __str__(self):
        return '\n'.join(f'{address}\n{stat}' for address, stat in self.address_stat.items())


class StatManager:
    def __init__(self):
        self.stats = []

    def add_statistics(self, stat):
        self.stats.append(stat)

    def update(self, packet):
        for stat in self.stats:
            stat.update(packet)

    def calculate(self):
        for stat in self.stats:
            stat.calculate()

    def get_values(self):
        return [stat.get_value() for stat in self.stats]

    def __str__(self):
        return '\n'.join(map(str, self.stats))


class Stat:
    def update(self, packet):
        pass

    def calculate(self):
        pass

    def get_value(self):
        pass


class MaxTimeStat(Stat):
    def __init__(self):
        self.max = float('-inf')

    def update(self, packet):
        if packet.time > self.max:
            self.max = packet.time

    def get_value(self):
        return self.max

    def __str__(self):
        if self.max != float('-inf'):
            return 'Max time: {}'.format(self.max)
        return 'Max time: Not calculated'


class MinTimeStat(Stat):
    def __init__(self):
        self.min = float('+inf')

    def update(self, packet):
        if packet.time < self.min:
            self.min = packet.time

    def get_value(self):
        return self.min

    def __str__(self):
        if self.min != float('+inf'):
            return 'Min time: {}'.format(self.min)
        return 'Min time: Not calculated'


class AverageTimeStat(Stat):
    def __init__(self):
        self.sum = 0
        self.count = 0
        self.result = 0

    def update(self, packet):
        self.sum += packet.time
        self.count += 1

    def calculate(self):
        self.result = self.sum / self.count

    def get_value(self):
        return self.result

    def __str__(self):
        if self.result:
            return 'Average time: {}'.format(self.result)
        return 'Average time: Not calculated'
