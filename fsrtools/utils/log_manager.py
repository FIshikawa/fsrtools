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
        if cout_tag is False and log_file is None and silent is False:
            raise ValueError('log_file is defined nesessarily' \
                              'when cout_tag is False.')
        if log_file is not None:
            if os.path.exists(log_file):
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
        if increase_number:
            self.indent += increase_number
        else:
            self.indent += 1
        self.temp_indent = self.indent

    def decrease_indent(self,decrease_number=0):
        if decrease_number:
            self.indent -= decrease_number
        else:
            self.indent -= 1
        self.temp_indent = self.indent

    def __call__(self,sentence,log_file_temp=None,end='\n'):
        if isinstance(sentence,str):
            sentence = self.__indent() + sentence
        else:
            sentence = self.__indent() + '{}'.format(sentence)
        if log_file_temp is None and self.log_file is not None:
            f = open(self.log_file,'a')
            f.write(sentence + end)
            f.close()
        elif log_file_temp is not None:
            f = open(log_file_temp,'a')
            f.write(sentence + end)
            f.close()
        if self.cout_tag:
            print(sentence,end=end)
        if end != '\n':
            self.indent = 0
        else:
            self.indent = self.temp_indent

    def progress_bar(self,loop,loop_max,add_sentence=None,indent=0):
        if not self.silent:
            sys.stdout.write('\r')
            sentence = ''
            if indent > 0:
                for i in range(indent):
                    sentence += '  ' 
            else:
                for i in range(self.indent):
                    sentence += '  ' 
            progress_ratio = int(float(loop+1)/float(loop_max)*100)
            sentence += '[Progress : {0:0=3}%]'.format(progress_ratio)
            if add_sentence != None:
                sentence += add_sentence
            sys.stdout.write(sentence)
            sys.stdout.flush()
            if progress_ratio >= 100:
                sys.stdout.write('\n')



