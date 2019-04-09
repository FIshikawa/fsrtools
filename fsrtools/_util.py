class LogManager:
    def __init__(self,indent=0,log_file=None,cout=False):
        self.__log_file_name = log_file
        self.__nest_number = indent
        self.__cout = cout

    def __set_indent_str(self):
        indent_str = ''
        for i in range(self.__nest_number):
            indent_str += '  ' 
        return indent_str

    def __reset_indent(self):
        self.__nest_number = 0
    def __add_indent(self):
        self.__nest_number += 1
    def __decrease_indent(self):
        self.__nest_number -= 1
    
    def log_write(self,sentence,temp_log_file_name=None):
        indent_str = self.__set_indent_str()
        sentence = indent_str + sentence
        if(temp_log_file_name is None and self.__log_file_name is not None):
            f = open(self.__log_file_name,"a")
            f.write(sentence + '\n')
            f.close()
        elif(temp_log_file_name is not None):
            f = open(temp_log_file_name,"a")
            f.write(sentence + '\n')
            f.close()
        if(self.__cout):
            print(sentence)
    
