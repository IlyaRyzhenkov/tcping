import unittest
from resouces import Statistics


class FPacket:
    def __init__(self, time):
        self.time = time
        self.is_answered = False
        self.send_time = 0

    def __eq__(self, other):
        return self.time == other.time and self.is_answered == other.is_answered and self.send_time == other.send_time

    def __copy__(self):
        return FPacket(self.time)


class TestStatistic(unittest.TestCase):
    PACKETS = [FPacket(2.0), FPacket(1.0), FPacket(33.0), FPacket(4.0)]

    def test_min_stat(self):
        stat = Statistics.MinTimeStat()
        for packet in self.PACKETS:
            stat.update_on_receive(packet)
        stat.calculate()
        self.assertEqual(stat.get_value(), 1.0, "Wrong min time stat")

    def test_max_stat(self):
        stat = Statistics.MaxTimeStat()
        for packet in self.PACKETS:
            stat.update_on_receive(packet)
        stat.calculate()
        self.assertEqual(stat.get_value(), 33.0, "Wrong max time stat")

    def test_average_stat(self):
        stat = Statistics.AverageTimeStat()
        for packet in self.PACKETS:
            stat.update_on_receive(packet)
        stat.calculate()
        self.assertEqual(stat.get_value(), 10.0, "Wrong average time stat")

    def test_stat_manager(self):
        manager = Statistics.StatManager()
        min_stat = Statistics.MinTimeStat()
        max_stat = Statistics.MaxTimeStat()
        manager.add_statistics(min_stat)
        manager.add_statistics(max_stat)
        for packet in self.PACKETS:
            manager.update_on_receive(packet)
        manager.calculate()
        res = manager.get_values()
        self.assertListEqual(res, [1.0, 33.0], "Wrong stat manager")

    def test_address_stat_manager(self):
        manager = Statistics.AddressStatManager((
            Statistics.MaxTimeStat, Statistics.MinTimeStat, Statistics.AverageTimeStat))
        manager.add_address(('1.1.1.1', 80))
        manager.add_address(('2.2.2.2', 80))
        manager.update_on_receive(('1.1.1.1', 80), FPacket(10))
        manager.update_on_receive(('1.1.1.1', 80), FPacket(6))
        manager.update_on_receive(('2.2.2.2', 80), FPacket(300))
        manager.calculate()
        res = manager.get_values()
        self.assertEqual(res[0][0], ('1.1.1.1', 80), 'Wrong first addr')
        self.assertListEqual(res[0][1].get_values(), [10, 6, 8.0], 'Wrong stat for first addr')
        self.assertEqual(res[1][0], ('2.2.2.2', 80), 'Wrong second addr')
        self.assertListEqual(res[1][1].get_values(), [300, 300, 300.0], 'Wrong stat for second addr')

    def test_add_stat(self):
        manager = Statistics.AddressStatManager((Statistics.MaxTimeStat,))
        manager.add_address(('1.1.1.1', 80))
        manager.update_on_receive(('1.1.1.1', 80), FPacket(10))
        manager.add_stat(Statistics.MinTimeStat)
        manager.update_on_receive(('1.1.1.1', 80), FPacket(300))
        res = manager.get_values()
        self.assertListEqual(res[0][1].get_values(), [300, 300], 'Wrong add stat')
