import os 
import json
import fsrtools

from fsrtools.utils import LogManager
from fsrtools.utils import SettingManager
from fsrtools.utils.colors import *

def _commands_json_file(test=False):
    if test:
        return os.path.join(fsrtools.__path__[0],
                            'config/commands_test.json')
    else:
        return os.path.join(fsrtools.__path__[0],
                            'config/commands.json')


class CommandManager:
    def __init__(self):
        self._json_path = _commands_json_file()
        if os.path.exists(self._json_path):
            commands_json = open(self._json_path)
            self.command_data = json.load(commands_json)
            self.command_name_list = list(self.command_data.keys())
        else:
            self.command_data = {}
            self.command_name_list= []

    def command_list(self):
        for i in range(len(self.command_name_list)):
            command_name = self.command_name_list[i]
            print('[{0}] command name : {1} '.format(i,command_name))
            print('  {}'.format(self.command_data[command_name]))

    def command(self,command_id):
        if isinstance(command_id,int):
            return self.command_data[self.command_name_list[command_id]]
        elif isinstance(command_id, str):
            return self.command_data[command_id]
        else:
            raise ValueError('input is string or int')

    def add_command(self,command_dict):
        for key in command_dict.keys():
            if key in self.command_data.keys():
                color_print('Error : command "{0}" is already registered'.format(key),'RED')
            else:
                print('add command "{0}"'.format(key))
                print(command_dict)
                self.command_data[key] = command_dict[key]
                self.command_name_list = list(self.command_data.keys())

    def remove_command(self,command_name):
        if command_name in self.command_data.keys():
            print('command {0} is removed'.format(command_name))
            del self.command_data[command_name]
            self.command_name_list = list(self.command_data.keys())
        else:
            color_print('Error : command {0} is not registered'.format(command_name),'RED')

    def save(self):
        print('save now defined commands')
        f = open(self._json_path,'w')
        json.dump(self.command_data,f,indent=4)
        f.close()

    def export(self):
        current_directory = os.getcwd()
        print('exprot commands.json in current directory')
        f = open(os.path.join(current_directory,'commands.json'),'w')
        json.dump(self.command_data,f,indent=4)
        f.close()
