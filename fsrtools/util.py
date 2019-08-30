import json
import datetime
import time 
import os
import sys


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

    def __init__(self,n_indent=0,log_file=None,cout_tag=False,silent=False):
        if(cout_tag is False and log_file is None and silent is False):
            raise ValueError('log_file is defined nesessarily when cout_tag is False.')
        if(log_file is not None):
            if(os.path.exists(log_file)):
                os.remove(log_file)
        self.log_file = log_file
        self.indent = n_indent
        self.temp_indent = n_indent
        self.cout_tag = cout_tag
        self.silent = silent

    def __indent(self):
        indent_str = ''
        for i in range(self.indent):
            indent_str += '  ' 
        return indent_str

    def reset_indent(self):
        self.indent = 0
        self.temp_indent = 0

    def add_indent(self,increase_number=0):
        if(increase_number):
            self.indent += increase_number
        else:
            self.indent += 1
        self.temp_indent = self.indent

    def decrease_indent(self,decrease_number=0):
        if(decrease_number):
            self.indent -= decrease_number
        else:
            self.indent -= 1
        self.temp_indent = self.indent

    def __call__(self,sentence,log_file_temp=None,end='\n'):
        if(isinstance(sentence,str)):
            sentence = self.__indent() + sentence
        else:
            sentence = self.__indent() + '{}'.format(sentence)
        if(log_file_temp is None and self.log_file is not None):
            f = open(self.log_file,'a')
            f.write(sentence + end)
            f.close()
        elif(log_file_temp is not None):
            f = open(log_file_temp,'a')
            f.write(sentence + end)
            f.close()
        if(self.cout_tag):
            print(sentence,end=end)
        if(end != '\n'):
            self.indent = 0
        else:
            self.indent = self.temp_indent

    def progress_bar(self,loop,loop_max,add_sentence=None,indent=0):
        if(not self.silent):
            sys.stdout.write('\r')
            sentence = ''
            if(indent > 0):
                for i in range(indent):
                    sentence += '  ' 
            else:
                for i in range(self.indent):
                    sentence += '  ' 
            progress_ratio = int(float(loop+1)/float(loop_max)*100)
            sentence += '[Progress : {0:0=3}%]'.format(progress_ratio)
            if(add_sentence != None):
                sentence += add_sentence
            sys.stdout.write(sentence)
            sys.stdout.flush()
            if(progress_ratio >= 100):
                sys.stdout.write('\n')


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




