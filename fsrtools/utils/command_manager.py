import os 
import json
import fsrtools

def _commands_json_file(test=False):
    if(test):
        return os.path.join(fsrtools.__path__[0],
                            'config/commands_test.json')
    else:
        return os.path.join(fsrtools.__path__[0],
                            'config/commands.json')


class CommandManager:
    def __init__(self,test=False):
        self._json_path = _commands_json_file(test)
        if(os.path.exists(self._json_path)):
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
        if(isinstance(command_id,int)):
            return self.command_data[self.command_name_list[command_id]]
        elif(isinstance(command_id, str)):
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

    def test_simulate(self,command_id,execute_part):
        if(isinstance(command_id,int)):
            command_name =  self.command_name_list[command_id]
        elif(not command_id in self.command_name_list):
            raise ValueError('not find {} in registered commands'.format(command_name))
        else:
            command_name = command_id
        for key in execute_part:
            if(not key in self.command_data[command_name]):
                raise ValueError('{0} is not execute file part in {1}'.format(execute_part,command_name))
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
        execute_simulation(command_name,simulate_params,result_directory,log_write,self.command_data)
        files_list_created = os.listdir('./test/')
        for key in list(set(files_list_created) - set(files_list)):
            os.remove(os.path.join('./test',key))
        print('test simulate end')


