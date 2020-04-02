import pytest
import os 
import json
from fsrtools.utils import CommandManager
from fsrtools.utils.command_manager import _commands_json_file

class CommandManagerTest(CommandManager):
    def __init__(self,test=True):
        super(CommandManager,self).__init__()
        self._json_path = _commands_json_file(test=True)
        if(os.path.exists(self._json_path)):
            commands_json = open(self._json_path)
            self.command_data = json.load(commands_json)
            self.command_name_list = list(self.command_data.keys())
        else:
            self.command_data = {}
            self.command_name_list= []

def test_CommandManager():
    files_list = os.listdir('./test/')
    command_manager = CommandManagerTest()
    if('hello_world' in command_manager.command_name_list):
        print('hello_world is already set : remove for initialization ')
        command_manager.remove_command('hello_world')
    command_manager.add_command({'hello_world' : ['python','./test/hello_world.py','N_loop']})
    command_manager.save()
    command_manager.command_list()
    command_manager.test_simulate('hello_world',['python','./test/hello_world.py'])
    files_list_created = os.listdir('./test/')
    for key in list(set(files_list_created) - set(files_list)):
        os.remove(os.path.join('./test',key))

