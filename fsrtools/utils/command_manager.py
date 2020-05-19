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
            print('[saved commands exists]')
            commands_json = open(self._json_path)
            self.command_data = json.load(commands_json)
            self.command_name_list = list(self.command_data.keys())
        else:
            print('[No saved commands]')
            self.command_data = {}
            self.command_name_list= []

    def view_command_list(self):
        '''Function to view registered command list .
        '''
        print('[Registered commands]')
        print(' print as " [number] : name ".')
        for i in range(len(self.command_name_list)):
            command_name = self.command_name_list[i]
            print('  [{0}] : {1} '.format(i,command_name))

    def view_command(self, command_id):
        '''Function to veiw the detail of commands.
        This function print the explicit executable comannd,  

        Args:
            command_id (int or string) : The tag or name of command.
        '''
        command_name = None
        if isinstance(command_id,int):
            command_name = self.command_name_list[command_id]
        else:
            command_name = command_id
        print('command name : {}'.format(command_name))
        print('  {}'.format(self.command(command_id)))

    def command(self,command_id):
        '''Function to return the detail of the commnad as list.

        Args:
            command_id (int or string) : The tag or name of command.
        Return:
            command_data (list) : List value of the detail of command.
        '''
        if isinstance(command_id,int):
            return self.command_data[self.command_name_list[command_id]]
        elif isinstance(command_id, str):
            return self.command_data[command_id]
        else:
            raise ValueError('input is string or int')

    def add_command(self,command_dict):
        '''Function to add commnad.

        Args:
            command_dict (dict) : The dictionary of comammnd to be added.
                                  The key is the name of command.
                                  The value is a list describing the 
                                        executalble command line.
        '''
        for key in command_dict.keys():
            if key in self.command_data.keys():
                color_print('Error : command "{0}" is already registered'
                            .format(key),'RED')
            else:
                print('add command "{0}"'.format(key))
                print(command_dict)
                self.command_data[key] = command_dict[key]
                self.command_name_list = list(self.command_data.keys())

    def remove_command(self,command_name):
        '''Function to remove a recorded commnad.

        Args:
            command_name (string) : The name of command.
        '''
        if command_name in self.command_data.keys():
            print('command {0} is removed'.format(command_name))
            del self.command_data[command_name]
            self.command_name_list = list(self.command_data.keys())
        else:
            color_print('Error : command {0} is not registered'
                        .format(command_name),'RED')

    def save(self):
        '''Function to save the added commands..
            If you forget this function, you cannot register the commands 
            added in this interactive shell.
        '''
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

