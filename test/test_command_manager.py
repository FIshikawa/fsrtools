import pytest
import re
import os 
import json
import subprocess
from fsrtools.utils import CommandManager
from fsrtools.utils import LogManager
from fsrtools.utils import SettingManager
from fsrtools.simulation_tools._manager_utils import set_execute_command
from fsrtools.utils.command_manager import _commands_json_file

class CommandManagerTest(CommandManager):
    def __init__(self):
        super(CommandManager,self).__init__()
        self._json_path = _commands_json_file(test=True)
        if(os.path.exists(self._json_path)):
            commands_json = open(self._json_path)
            self.command_data = json.load(commands_json)
            self.command_name_list = list(self.command_data.keys())
        else:
            self.command_data = {}
            self.command_name_list= []

    def test_simulate(self,command_id,execute_part):
        if(isinstance(command_id,int)):
            command_name =  self.command_name_list[command_id]
        elif(not command_id in self.command_name_list):
            raise ValueError('not find {} in registered commands'
                                .format(command_name))
        else:
            command_name = command_id
        for key in execute_part:
            if(not key in self.command_data[command_name]):
                raise ValueError('{0} is not execute file part in {1}'
                                    .format(execute_part,command_name))
        print('test simulate : {}'.format(command_name))
        result_directory = './test/'
        files_list = os.listdir('./test/')
        print('result directory : {}'.format(result_directory))
        log_file = 'log.dat'
        print('log file name : {}'.format(log_file))
        log_file = os.path.join(result_directory, log_file)
        print('log file path : {}'.format(log_file))
        log_write = LogManager(log_file=log_file,cout_tag=True)
        setting_manager = SettingManager(log_write) 
        setting_manager.set_directory(result_directory)
        print('all parameters are set 1 unifromaly')
        simulate_params = {}
        for key in self.command_data[command_name]:
            if(key == 'result_directory'):
                simulate_params[key] = result_directory
            elif(key in execute_part):
                simulate_params[key] = key
            else:
                simulate_params[key] = '1'

        execute_command = set_execute_command(command_name,
                                              simulate_params,
                                              log_write,
                                              self.command_data)
        p = subprocess.Popen(execute_command)
        p.wait()
        return_value = p.wait()

        files_list_created = os.listdir('./test/')
        for key in list(set(files_list_created) - set(files_list)):
            os.remove(os.path.join('./test',key))
        print('test simulate end')


def test_CommandManager():
    files_list = os.listdir('./test/')
    command_manager = CommandManagerTest()
    if('hello_world' in command_manager.command_name_list):
        print('hello_world is already set : remove for initialization ')
        command_manager.remove_command('hello_world')
    command_manager.add_command({'hello_world' : 
                                ['python','./test/hello_world.py','N_loop']})
    command_manager.save()
    command_manager.view_command_list()
    command_manager.test_simulate('hello_world',
                                  ['python','./test/hello_world.py'])
    files_list_created = os.listdir('./test/')
    for key in list(set(files_list_created) - set(files_list)):
        os.remove(os.path.join('./test',key))

