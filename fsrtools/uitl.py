import json
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
            f = open(self.log_file,"a")
            f.write(sentence + '\n')
            f.close()
        elif(log_file_temp is not None):
            f = open(log_file_temp,"a")
            f.write(sentence + '\n')
            f.close()
        if(self.__cout_tag):
            print(sentence)


class StopWatch:
    """
    Stop watch class : work as function object 

    Args:

    Attributes :

    """


    def __init__(self):
        self.start_time = None 
        self.end_time = None 
        self.duration = None 
        self.lap_start = None 
        self.lap_end = None 
        self.split_time = None

    def start(self):
        self.start_time = time.time()
        start_time_cnv = time.strptime(time.ctime(self.start_time))
        return time.strftime("%Y/%m/%d %H:%M:%S", start_time_cnv)

    def end(self):
        self.end_time = time.time()
        end_time_cnv = time.strptime(time.ctime(self.end_time))
        return time.strftime("%Y/%m/%d %H:%M:%S", end_time_cnv)

    def duration(self):
        self.duration = self.end_time - self.start_time
        time_duration_cnv = time.gmtime(self.duration)
        return time.strftime("%d:%H:%M:%S", time_duration_cnv)

    def lap_start(self):
        self.lap_start = time.time()
        start_time_cnv = time.strptime(time.ctime(self.lap_start))
        return time.strftime("%Y/%m/%d %H:%M:%S", start_time_cnv)

    def lap_end(self):
        self.lap_end = time.time()
        end_time_cnv = time.strptime(time.ctime(self.lap_end))
        return time.strftime("%Y/%m/%d %H:%M:%S", start_time_cnv)

    def lap_time(self):
        time_duration = self.lap_end - self.lap_start
        time_duration_cnv = time.gmtime(time_duration)
        return time.strftime("%d:%H:%M:%S", time_duration_cnv)

    def split_time(self):
        lap_temp = time.time()
        time_duration = lap_temp - self.start_time
        time_duration_cnv = time.gmtime(time_duration)
        return time.strftime("%d:%H:%M:%S", time_duration_cnv)

    def nowtime(self):
        return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")


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
          log_manager('[Create : {}]'.format(directory_name))
        else:
          log_manager('[Already exist]')

    def json_set(self,parameter_dict,file_name):
        f = open(file_name,'w')
        json.dump(parameter_dict,f,indent=4)
        f.close()

