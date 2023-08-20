import threading
import time
from collections import namedtuple

import psutil
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QPainter

CPU_STATUS = namedtuple("CPU_STATUS", "count, count_logical, percent, tot_percent, freq, times, times_percent, stat")

def get_cpu_status():

    cpu_count = psutil.cpu_count(False)
    cpu_count_logical = psutil.cpu_count()
    cpu_tot_percent = psutil.cpu_percent(0.5)
    cpu_percent = psutil.cpu_percent(0.5, True)
    cpu_freq = psutil.cpu_freq(True)
    cpu_times = psutil.cpu_times()
    cpu_times_percent = psutil.cpu_times_percent(1)
    cpu_stat = psutil.cpu_stats()
    return CPU_STATUS(cpu_count, cpu_count_logical, cpu_percent, cpu_tot_percent, cpu_freq, cpu_times, cpu_times_percent, cpu_stat)

class CPU_Monitor():

    def __init__(self, count:int=1):

        self.tot_percent:list[float] = []
        self.percent:list[list[float]] = []
        for i in range(count):
            self.percent.append([])
        self.freq:list[float] = []
        self.axisX = QValueAxis()
        self.axisX.setTitleText("")
        self.axisX.setTickCount(11)
        self.axisX.setMin(0)
        self.axisX.setMax(10)
        self.axisX.setLabelFormat("%d")
        self.axisY = QValueAxis()
        self.axisY.setTitleText("CPU 占用率 (%)")
        self.axisY.setTickCount(5)
        self.axisY.setMin(0)
        self.axisY.setMax(100)
        self.axisY.setLabelFormat("%d")
        self.axisY2 = QValueAxis()
        self.axisY2.setTitleText("CPU 频率 (Mhz)")
        self.axisY2.setTickCount(5)
        self.axisY2.setMin(0)
        self.axisY2.setMax(100)
        self.axisY2.setLabelFormat("%d")
        self.chart = QChart()
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.chart.addAxis(self.axisY, Qt.AlignLeft)
        self.chart.addAxis(self.axisY2, Qt.AlignRight)
        # self.chart.legend().setAlignment(Qt.AlignRight)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.tot_series = QLineSeries()
        self.tot_series.setName("CPU 总占用率")
        self.tot_series.setBrush(QBrush(Qt.blue))
        self.chart.addSeries(self.tot_series)
        self.tot_series.attachAxis(self.axisX)
        self.tot_series.attachAxis(self.axisY)
        self.freq_series = QLineSeries()
        self.freq_series.setName("CPU 频率")
        self.chart.addSeries(self.freq_series)
        self.freq_series.attachAxis(self.axisX)
        self.freq_series.attachAxis(self.axisY2)
        self.chartview = QChartView()
        self.chartview.setChart(self.chart)
        self.chartview.setRenderHint(QPainter.Antialiasing)
    
    def push(self, tot_percent:float, freq:float):

        if len(self.tot_percent) == 11:
            self.tot_percent.pop(0)
        self.tot_percent.append(tot_percent)
        self.tot_series.setName(f"CPU 总占用率 [{tot_percent} %]")
        self.tot_series.clear()
        if len(self.freq) == 11:
            self.freq.pop(0)
        self.freq.append(freq)
        self.freq_series.setName(f"CPU 频率 [{freq} Mhz]")
        self.axisY2.setMax(max(self.freq)*1.1)
        self.freq_series.clear()
        for i in range(len(self.tot_percent)):
            self.tot_series.append(i, self.tot_percent[i])
        for i in range(len(self.freq)):
            self.freq_series.append(i, self.freq[i])

def get_memory_status():

    memory_info = psutil.virtual_memory()
    return memory_info

def get_pids():

    return psutil.pids()

class Monitor(threading.Thread):

    def __init__(self):

        super(Monitor, self).__init__()
        self.chunk = 1
        self.locked = True
        self.processes = []
        self.working = False

    def run(self):

        self.cpu_count = psutil.cpu_count()
        while self.working:
            self.locked = True
            self.processes = []
            for proc in psutil.process_iter():
                try:
                    self.processes.append(proc.as_dict(attrs=["pid", "name", "cpu_percent", "memory_percent"]))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            self.locked = False
            time.sleep(self.chunk)

if __name__ == "__main__":
    monitor = Monitor()
    monitor.start()
    # monitor.join()
    while monitor.is_alive():
        while monitor.locked:
            time.sleep(0.1)
        print(monitor.processes)