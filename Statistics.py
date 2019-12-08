class StatManager:
    def __init__(self):
        self.stats = []

    def add_statistics(self, stat):
        self.stats.append(stat)

    def calculate(self, packets):
        for packet in packets:
            for stat in self.stats:
                stat.update(packet)
        for stat in self.stats:
            stat.calculate()

    def __str__(self):
        return '\n'.join(str(stat) for stat in self.stats)


class Stat:
    def update(self, packet):
        pass

    def calculate(self):
        pass


class MaxTimeStat(Stat):
    def __init__(self):
        self.max = float('-inf')

    def update(self, packet):
        if packet.time > self.max:
            self.max = packet.time

    def __str__(self):
        return 'Max time: {}'.format(self.max)


class MinTimeStat(Stat):
    def __init__(self):
        self.min = float('+inf')

    def update(self, packet):
        if packet.time < self.min:
            self.min = packet.time

    def __str__(self):
        return 'Min time: {}'.format(self.min)


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

    def __str__(self):
        return 'Average time: {}'.format(self.result)
