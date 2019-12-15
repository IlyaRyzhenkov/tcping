import unittest
import Statistics


class FPacket:
    def __init__(self, time):
        self.time = time


class TestStatistic(unittest.TestCase):
    PACKETS = [FPacket(2.0), FPacket(1.0), FPacket(33.0), FPacket(4.0)]

    def test_min_stat(self):
        stat = Statistics.MinTimeStat()
        for packet in self.PACKETS:
            stat.update(packet)
        stat.calculate()
        self.assertEqual(stat.get_value(), 1.0, "Wrong min time stat")

    def test_max_stat(self):
        stat = Statistics.MaxTimeStat()
        for packet in self.PACKETS:
            stat.update(packet)
        stat.calculate()
        self.assertEqual(stat.get_value(), 33.0, "Wrong max time stat")

    def test_average_stat(self):
        stat = Statistics.AverageTimeStat()
        for packet in self.PACKETS:
            stat.update(packet)
        stat.calculate()
        self.assertEqual(stat.get_value(), 10.0, "Wrong average time stat")

    def test_stat_manager(self):
        manager = Statistics.StatManager()
        min_stat = Statistics.MinTimeStat()
        max_stat = Statistics.MaxTimeStat()
        manager.add_statistics(min_stat)
        manager.add_statistics(max_stat)
        for packet in self.PACKETS:
            manager.update(packet)
        manager.calculate()
        res = manager.get_values()
        self.assertListEqual(res, [1.0, 33.0], "Wrong stat manager")
