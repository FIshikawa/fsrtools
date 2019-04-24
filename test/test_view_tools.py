import shutil
import json
import os
import pytest
import fsrtools.view_tools as fsrview 
import fsrtools.simulate_tools as fsrsimulate

class CommandManagerTest(fsrsimulate.CommandManager):
    def __init__(self):
        super(fsrsimulate.CommandManager,self).__init__()
        self._json_path = fsrsimulate._commands_json_file(test=True)
        if(os.path.exists(self._json_path)):
            commands_json = open(self._json_path)
            self.command_data = json.load(commands_json)
            self.command_name_list = list(self.command_data.keys())
        else:
            self.command_data = {}
            self.command_name_list= []


@pytest.fixture(scope='module')
def set_data_for_test():
    files_list = os.listdir('./test/')
    command_manager = CommandManagerTest()
    if('hello_world' in command_manager.command_name_list):
        command_manager.remove_command('hello_world')
    command_manager.add_command({'hello_world' : ['python','./test/hello_world.py','N_loop']})
    command_manager.save()
    log_file = 'test/log.dat'
    parameter_json = 'test/parameter_test.json'
    command_data = command_manager.command_data
    fsrsimulate.operate_experiments(parameter_file=parameter_json,log_file=log_file,test_mode=False,command_data=command_data)
    yield set_data_for_test
    command_manager.save()
    files_list_created = os.listdir('./test/')
    for key in list(set(files_list_created) - set(files_list)):
        try:
            os.remove(os.path.join('./test',key))
        except OSError as now_error:
            shutil.rmtree(os.path.join('./test',key))


def test_set_data_map(set_data_for_test):
    top_directory = ''
    with os.scandir('./test') as files:
        for entry in files:
            if '-' in entry.name and entry.is_dir():
                top_directory = entry.name
                break
    top_directory = os.path.join('./test',top_directory)
    print(top_directory)
    config_data_map, result_data_map = fsrview.set_data_map(top_directory)
    print(config_data_map)
    print(result_data_map)


