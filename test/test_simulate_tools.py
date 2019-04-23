import unittest 
import shutil
import os
import fsrtools.simulate_tools as fsrsimulate

class TestSimulateTools(unittest.TestCase):
    def test_CommandManager(self):
        files_list = os.listdir('./test/')
        command_manager = fsrsimulate.CommandManagerTest()
        if('hello_world' in command_manager.command_name_list):
            print('hello_world is already set : remove for initialization ')
            command_manager.remove_command('hello_world')
        command_manager.add_command({'hello_world' : ['python','./test/hello_world.py','N_loop']})
        command_manager.save()
        command_manager.test_simulate('hello_world',['python','./test/hello_world.py'])
        files_list_created = os.listdir('./test/')
        for key in list(set(files_list_created) - set(files_list)):
            os.remove(os.path.join('./test',key))

    def test_operate_experiments(self):
        files_list = os.listdir('./test/')
        command_manager = fsrsimulate.CommandManager()
        if('hello_world' in command_manager.command_name_list):
            print('hello_world is already set : remove for initialization ')
            command_manager.remove_command('hello_world')
        command_manager.add_command({'hello_world' : ['python','./test/hello_world.py','N_loop']})
        command_manager.save()
        log_file = 'log.dat'
        parameter_json = 'test/parameter_test.json'
        fsrsimulate.operate_experiments(parameter_file=parameter_json,log_file=log_file,test_mode=True)
        command_manager.remove_command('hello_world')
        command_manager.save()
        files_list_created = os.listdir('./test/')
        for key in list(set(files_list_created) - set(files_list)):
            try:
                os.remove(os.path.join('./test',key))
            except OSError as now_error:
                shutil.rmtree(os.path.join('./test',key))

if __name__ == "__main__":
    unittest.main()

