import datetime 
import time

class StopWatch:
    """
    Stop watch class : work as function object 

    """

    def __init__(self):
        self._start_time = None 
        self._end_time = None 
        self._duration = None 
        self._lap_start = None 
        self._lap_end = None 
        self._split_time = None

    def start(self):
        self._start_time = time.time()
        start_time_cnv = time.localtime(self._start_time)
        return time.strftime('%Y/%m/%d %H:%M:%S', start_time_cnv)

    def start_time(self,format=None):
        start_time_cnv = time.localtime(self._start_time)
        if format is None: 
            return time.strftime('%Y/%m/%d %H:%M:%S', start_time_cnv)
        else:
            return time.strftime(format, start_time_cnv)

    def end(self,format=None):
        self._end_time = time.time()
        end_time_cnv = time.localtime(self._end_time)
        return time.strftime('%Y/%m/%d %H:%M:%S', end_time_cnv)

    def end_time(self, format=None):
        end_time_cnv = time.localtime(self._end_time)
        if format is None: 
            return time.strftime('%Y/%m/%d %H:%M:%S', end_time_cnv)
        else:
            return time.strftime(format, start_time_cnv)

    def duration(self):
        self._duration = datetime.timedelta(seconds=self._end_time - self._start_time)
        return str(self._duration)

    def lap_start(self):
        self._lap_start = time.time()
        start_time_cnv = time.localtime(self._lap_start)
        return time.strftime('%Y/%m/%d %H:%M:%S', start_time_cnv)

    def lap_end(self):
        self._lap_end = time.time()
        end_time_cnv = time.localtime(self._lap_end)
        return time.strftime('%Y/%m/%d %H:%M:%S', end_time_cnv)

    def lap_time(self):
        time_duration = datetime.timedelta(seconds=self._lap_end - self._lap_start)
        return str(time_duration)

    def split_time(self):
        lap_temp = time.time()
        time_duration = datetime.timedelta(seconds=lap_temp - self._lap_start)
        return str(time_duration)

    def nowtime(self):
        return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')


