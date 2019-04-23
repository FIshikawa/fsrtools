import json
import datetime
import time 
import os


class LogManager:
    """
    Log print manager class : work as function object 

    Args:
        indent:
            number of indent of log print
        log_file:
            path of log file 
        cout_tag:
            flag of standard output  

    Attributes :
        indent:
            number of indent of log print
        log_file:
            path of log file 
        cout_tag:
            flag of standard output  

    """

    def __init__(self,indent=0,log_file=None,cout_tag=False):
        if(cout_tag is False and log_file is None):
            raise ValueError('log_file is defined nesessarily when cout_tag is False.')
        if(os.path.exists(log_file)):
            os.remove(log_file)
        self.log_file = log_file
        self.indent = indent
        self.cout_tag = cout_tag

    def __indent(self):
        indent_str = ''
        for i in range(self.indent):
            indent_str += '  ' 
        return indent_str

    def reset_indent(self):
        self.indent = 0
    def add_indent(self):
        self.indent += 1
    def decrease_indent(self):
        self.indent -= 1
    
    def __call__(self,sentence,log_file_temp=None):
        sentence = self.__indent() + sentence
        if(log_file_temp is None and self.log_file is not None):
            f = open(self.log_file,'a')
            f.write(sentence + '\n')
            f.close()
        elif(log_file_temp is not None):
            f = open(log_file_temp,'a')
            f.write(sentence + '\n')
            f.close()
        if(self.cout_tag):
            print(sentence)


class StopWatch:
    """
    Stop watch class : work as function object 

    Args:

    Attributes :

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
        if(format is None): 
            return time.strftime('%Y/%m/%d %H:%M:%S', start_time_cnv)
        else:
            return time.strftime(format, start_time_cnv)

    def end(self,format=None):
        self._end_time = time.time()
        end_time_cnv = time.localtime(self._end_time)
        return time.strftime('%Y/%m/%d %H:%M:%S', end_time_cnv)

    def end_time(self, format=None):
        end_time_cnv = time.localtime(self._end_time)
        if(format is None): 
            return time.strftime('%Y/%m/%d %H:%M:%S', end_time_cnv)
        else:
            return time.strftime(format, start_time_cnv)

    def duration(self):
        self._duration = datetime.timedelta(seconds=self._end_time - self._start_time)
        return str(self._duration)

    def lap_start(self):
        self.lap_start = time.time()
        start_time_cnv = time.localtime(self.lap_start)
        return time.strftime('%Y/%m/%d %H:%M:%S', start_time_cnv)

    def lap_end(self):
        self.lap_end = time.time()
        end_time_cnv = time.localtime(self.lap_end)
        return time.strftime('%Y/%m/%d %H:%M:%S', end_time_cnv)

    def lap_time(self):
        time_duration = datetime.timedelta(seconds=self.lap_end - self.lap_start)
        return str(time_duration)

    def split_time(self):
        lap_temp = time.time()
        time_duration = datetime.timedelta(seconds=lap_temp - self.start_time)
        return str(time_duration)

    def nowtime(self):
        return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')


class SettingManager:
    """
    Setting manager class, create directory , json file and so on

    Args:
        log_manager :
            LogManager class 

    Attributes :

    """


    def __init__(self,log_manager):
        self.__log_manager = log_manager

    def set_directory(self,directory_name):
        if(os.path.exists(directory_name) != True):
          os.mkdir(directory_name)
          self.__log_manager('[Create : {}]'.format(directory_name))
        else:
          self.__log_manager('[Already exist]')

    def json_set(self,parameter_dict,file_name):
        f = open(file_name,'w')
        json.dump(parameter_dict,f,indent=4)
        f.close()


def colors(color):
    colors_dict= {'BLACK'     : '\033[30m',
                  'RED'       : '\033[31m',
                  'GREEN'     : '\033[32m',
                  'YELLOW'    : '\033[33m',
                  'BLUE'      : '\033[34m',
                  'PURPLE'    : '\033[35m',
                  'CYAN'      : '\033[36m',
                  'WHITE'     : '\033[37m',
                  'END'       : '\033[0m' ,
                  'BOLD'      : '\038[1m' ,
                  'UNDERLINE' : '\033[4m' ,
                  'INVISIBLE' : '\033[08m',
                  'REVERCE'   : '\033[07m'
                  }
    return colors_dict[color]


def color_print(sentence,color):
    print(colors(color) + sentence + colors('END'))



