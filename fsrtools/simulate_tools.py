import os
import json
import copy
import shutil
import subprocess
from datetime import datetime
import fsrtools 
from fsrtools.util import StopWatch
from fsrtools.util import SettingManager
from fsrtools.util import LogManager
from fsrtools.util import colors
from fsrtools.util import color_print

def _commands_json_file(test=False):
    if(test):
        return os.path.join(fsrtools.__path__[0],'config/commands_test.json')
    else:
        return os.path.join(fsrtools.__path__[0],'config/commands.json')


def operate_experiments(parameter_file=None, log_file=None, cout_tag=False, test_mode=False):
    current_directory = os.getcwd()

    if(test_mode):
        log_file = 'test/log_test.dat'
        cout_tag = True

    log_file = os.path.join(current_directory, log_file)
    log_write = LogManager(log_file=log_file,cout_tag=cout_tag)
    setting_manager = SettingManager(log_write) 
    stop_watch = StopWatch()

    log_write('[start time : {}]'.format(stop_watch.start()))
    if(test_mode):
        log_write('[test mode]')
    log_write('[server name : {}]'.format('%s' % os.uname()[1]))
    log_write('[set log file at : {}]'.format(log_write.log_file))

    if(parameter_file is None):
        raise ValueError('parameter file must be set')
    log_write('[parameter file : {}]'.format(parameter_file))  
    json_file = open(parameter_file,'r')
    json_data = json.load(json_file)

    if(test_mode):
        if(json_data['experiment_dir'] != 'test/'): 
            log_write('[experiment_dir is not "test/" : force setting]')
            json_data['experiment_dir'] = 'test/'

    log_write('[paramter data info]')
    log_write('[result dir : {}]'.format(json_data['experiment_dir']))
    setting_manager.set_directory(json_data['experiment_dir'])
    log_write('[number of experiment : {}]'.format(len(json_data['experiments'].keys())))
    for key in json_data['experiments'].keys():
        log_write(' [{0} : number of simulate params: {1}]'.format(key, len(json_data['experiments'][key]['simulate_params'].keys())))

    if(test_mode):
        for key in json_data['experiments'].keys():
            log_write('[{0}]'.format(key))
            for key_t in json_data['experiments'][key].keys():
                log_write(' [{0}]'.format(key_t))
                for key_tt in json_data['experiments'][key][key_t].keys():
                    log_write('   {0} : {1}'.format(key_tt, json_data['experiments'][key][key_t][key_tt]))

    experiment_directory = os.path.join(json_data['experiment_dir'], stop_watch.start_time(format='%Y-%m-%d-%H-%M-%S') + '/')
    log_write('[set result output directory : {}]'.format(experiment_directory))
    setting_manager.set_directory(experiment_directory)

    json_data['time_info'] = {}
    json_data['time_info']['start_time'] = stop_watch.start_time()
    parameter_file_for_record = os.path.join(experiment_directory,'parameter.json')
    setting_manager.json_set(json_data, parameter_file_for_record)

    previous_key = ''
    experiment_tag = ''
    for key in json_data['experiments'].keys():
        log_write('[{0}][start experiment : {1}]'.format(key,stop_watch.lap_start()))
        log_write.add_indent()
        experiment_tag = key

        if('Same' in json_data['experiments'][key]['simulate_params'].keys()):
            if(len(previous_key) < 1):
                print('[Error ! : previous simulation does not exist !]')
                continue 
            key_list_temp = list(json_data['experiments'][key]['simulate_params'].keys())
            key_list_temp.remove('Same')
            value_dict_temp = {}
            for key_temp in key_list_temp:
                value_dict_temp[key_temp] = json_data['experiments'][key]['simulate_params'][key_temp]
            json_data['experiments'][key]['simulate_params'] = copy.deepcopy(json_data['experiments'][previous_key]['simulate_params'])
            for key_temp in key_list_temp:
                json_data['experiments'][key]['simulate_params'][key_temp] = value_dict_temp[key_temp] 

        json_data['experiments'][key]['experiment_params']['experiment_dir'] = experiment_directory
        operate_simulations(json_data['experiments'][key],experiment_tag,log_write)
        log_write.decrease_indent()
        log_write('[{0}][end experiment : {1} : lap time : {2}]'.format(key,stop_watch.lap_end(),stop_watch.lap_time()))
        previous_key = key

    log_write('[finish time : {}]'.format(stop_watch.end()))
    log_write('[duration : {}]'.format(stop_watch.duration()))
    json_data['time_info']['finish_time'] = stop_watch.end_time()
    json_data['time_info']['duration'] = stop_watch.duration()
    setting_manager.json_set(json_data, parameter_file_for_record)
    shutil.copy(log_file,os.path.join(experiment_directory,'log.dat'))


def operate_simulations(param_dict_original,experiment_tag,log_write):
    stop_watch = StopWatch()
    setting_manager = SettingManager(log_write) 

    param_dict = copy.deepcopy(param_dict_original)
    param_dict_original['experiment_params']['experiment_tag'] = experiment_tag 
    experiment_params = param_dict['experiment_params']
    simulate_params_original = param_dict['simulate_params']

    experiment_directory = experiment_params['experiment_dir']
    log_write('[check experiment directory : {}]'.format(experiment_directory))
    setting_manager.set_directory(experiment_directory)

    simulate_directory = os.path.join(experiment_directory,experiment_tag + '/') 
    log_write('[simulate directory : {}]'.format(simulate_directory))
    setting_manager.set_directory(simulate_directory)
    experiment_params['experiment_dir'] = simulate_directory
    
    param_dict_original['time_info'] = {}
    param_dict_original['time_info']['start_time'] = stop_watch.start()
    parameter_file_simulation = os.path.join(simulate_directory,'parameter.json')
    setting_manager.json_set(param_dict_original,parameter_file_simulation)

    command_name = experiment_params['command_name']

    simulate_params_original, total_combination = set_simulate_params_iterate_dict(simulate_params_original,log_write)

    simulate_number = 1
    commands_json = open(_commands_json_file())
    command_data = json.load(commands_json)
    if(len(total_combination) > 0):
        log_write('[total number of simulations : {}]'.format(len(total_combination)))
        log_write('[check iterate lists]')
        log_write('[iterate combination list] : {}'.format(total_combination))
    else:
        log_write('[total number of simulations : 1]')
        total_combination.append(['NO_ITERATION'])

    for i in range(max(len(total_combination),1)):
        if(len(total_combination) > 1):
            simulate_params = set_simulate_params(simulate_params_original, total_combination[i])
        else:
            simulate_params = simulate_params_original 
        log_write('[simulation : number-{}]'.format(simulate_number))
        log_write.add_indent()
        result_directory = os.path.join(simulate_directory,'number-' + str(simulate_number) + '/')
        setting_manager.set_directory(result_directory)
        execute_simulation(command_name,simulate_params,result_directory,log_write,command_data)
        simulate_number += 1
        log_write.decrease_indent()

    param_dict_original['time_info']['end_time'] = stop_watch.end()
    setting_manager.json_set(param_dict_original,parameter_file_simulation)
    log_write('[all simulations complete]')


def execute_simulation(command_name,simulate_params,result_directory,log_write,command_data): 
    stop_watch = StopWatch()
    setting_manager = SettingManager(log_write) 

    param_dict = {}
    param_dict['command_name'] = command_name
    param_dict['simulate_params'] = copy.deepcopy(simulate_params)
    param_dict['simulate_params']['result_directory'] = result_directory
    param_dict['time_info'] = {}
    param_dict['time_info']['start_time'] = stop_watch.start()
    execute_command = set_execute_command(command_name,param_dict['simulate_params'],log_write,command_data)

    parameter_file_each_simulation = os.path.join(result_directory, 'parameter.json')
    setting_manager.json_set(param_dict,parameter_file_each_simulation)

    log_write('[execute : {}]'.format(stop_watch.start_time()))
    log_open = open(log_write.log_file,'a')
    if(log_write.cout_tag):
        p = subprocess.Popen(execute_command)
    else:
        p = subprocess.Popen(execute_command,stdout=log_open,stderr=log_open)
    p.wait()
    log_open.close()
    return_value = p.wait()
    if(return_value != 0):
        log_write('[Abnormal termination detected : return_value : {}]'.format(return_value))
        reset_indent()
        log_write('[Error End !]')
        raise ValueError('[Abnormal termination detected : return_value : {}]'.format(return_value))

    log_write('[finish  : {}]'.format(stop_watch.end()))
    param_dict['time_info']['end_time'] = stop_watch.end_time()
    setting_manager.json_set(param_dict,parameter_file_each_simulation)


def set_execute_command(command_name,simulate_params,log_write,command_data):
    execute_command = []
    if(command_name in command_data.keys()):
        log_write('[detect : {}]'.format(command_name))
        command_list = command_data[command_name]
    else:
        log_write('[can not find !]')
        raise ValueError('{} is not defined as command'.format(command_name))

    for key in command_list:
        if(key in simulate_params.keys()):
            execute_command.append(str(simulate_params[key]))
        else:
            execute_command.append(key)
    log_write('[command_name line input]')
    log_write('{}'.format(execute_command))

    return execute_command


def product_combination_generator(iterate_dict):
    total_length = 1 
    length_dict = {}
    combination_list = []
    if(len(iterate_dict.keys()) > 0):
        for key in iterate_dict.keys():
            length_dict[key] = len(iterate_dict[key])
            total_length = total_length * len(iterate_dict[key])
        combination_list = [{} for x in range(total_length)]
        repeat_length = total_length
        previous_length = total_length
        for key, length in sorted(length_dict.items(), key=lambda x: -x[1]):
            repeat_length //= length
            for i in range(total_length):
                combination_list[i][key] = iterate_dict[key][ (i % previous_length) // repeat_length ]
            previous_length = repeat_length

    return combination_list 


def set_simulate_params_iterate_dict(simulate_params,log_write):
    simulate_params_temp = copy.deepcopy(simulate_params)
    iterate_dict = {}
    for key in simulate_params.keys():
        if(isinstance(simulate_params[key], list)):
            iterate_dict[key] = simulate_params[key]
            log_write('[list input : {0} : {1}]'.format(key, simulate_params[key]))
        elif(isinstance(simulate_params[key], str)):
            counter = 0
            local_variable_dict = {}
            for key_t in simulate_params.keys():
                if(key_t in simulate_params[key]):
                    if(isinstance(simulate_params[key_t], list) or isinstance(simulate_params[key_t],str)):
                        counter += 1
                    else:
                        local_variable_dict[key_t] = simulate_params[key_t]
                        counter += 1
            if(len(local_variable_dict) == counter):
                simulate_params_temp[key] = eval(simulate_params[key],globals(),local_variable_dict)
                log_write('[{0} : {1}]'.format(key, simulate_params[key]))
            else:
                for key_t in local_variable_dict.keys():
                    log_write('{0} is set at execute command set : depend on changing {1}'.format(key,key_t))

    total_combination = product_combination_generator(iterate_dict)
    return simulate_params_temp,  total_combination


def set_simulate_params(simulate_params,iterate_pair):
    for key in iterate_pair.keys():
        simulate_params[key] = iterate_pair[key]
    simulate_params_temp = copy.deepcopy(simulate_params)
    for key in simulate_params.keys():
        if(isinstance(simulate_params[key], str)):
            local_variable_dict = {}
            for key_t in simulate_params.keys():
                if(key_t in simulate_params[key]):
                    local_variable_dict[key_t] = simulate_params[key_t]
            print(local_variable_dict)
            simulate_params_temp[key] = eval(simulate_params[key],globals(),local_variable_dict)
    return simulate_params_temp


class CommandManager:
    def __init__(self):
        self._json_path = _commands_json_file()
        if(os.path.exists(self._json_path)):
            commands_json = open(self._json_path)
            self.command_data = json.load(commands_json)
            self.command_name_list = list(self.command_data.keys())
            self.command_list()
        else:
            self.coomands_data = {}
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
        print('test simulate end')


class CommandManagerTest(CommandManager):
    def __init__(self):
        super(CommandManager,self).__init__()
        self._json_path = _commands_json_file(test=True)
        if(os.path.exists(self._json_path)):
            commands_json = open(self._json_path)
            self.command_data = json.load(commands_json)
            self.command_name_list = list(self.command_data.keys())
            self.command_list()
        else:
            self.command_data = {}
            self.command_name_list= []


def time_log_print(dir,n_indent):
    sentence = ''
    indent_str = ''
    sub_indent_str = ''
    dir_name = dir.split('/')[-1]
    for i in range(n_indent):
        indent_str += '  ' 
    for i in range(n_indent+1):
        sub_indent_str += '  '
    if(os.path.exists(dir)):
        json_file = open(os.path.join(dir,'parameter.json'),'r')
        json_data = json.load(json_file)
        time_info = json_data['time_info']
        simulate_params = json_data['simulate_params']
        execute_file = json_data['experiment_params']['execute_file']
        simulate_params, iterate_dict , iterate_key_list, iterate_pair = set_simulate_params_iterate_dict(simulate_params,
                                                                                                       execute_file,
                                                                                                       log_write)
        if('start_time' in time_info.keys() and len(time_info['start_time']) > 0):
            start_time = time_info['start_time']
        else:
            start_time = 'wating'
        if('end_time' in time_info.keys() and len(time_info['end_time']) > 0):
          end_time = time_info['end_time']
          diff_time = datetime.strptime(end_time, '%Y/%m/%d %H:%M:%S') - datetime.strptime(start_time, '%Y/%m/%d %H:%M:%S')
          diff_time = diff_time.total_seconds()
          diff_time = '{0}h{1}m{2}s'.format(int(diff_time//3660), int(diff_time%3600//60), diff_time%3600%60)
          sentence = indent_str + '[{0}] : [start {1}] : [end {2}] : [duration {3}]'.format(dir_name,start_time,end_time,diff_time)
        else:
          ongoing_number = len([x for x in os.listdir(dir) if os.path.isdir(os.path.join(dir,x))])
          nowtime = datetime.now()
          diff_time = nowtime - datetime.strptime(start_time, '%Y/%m/%d %H:%M:%S')
          diff_time = diff_time.total_seconds()
          diff_time = '{0}h{1}m{2:.3g}s'.format(int(diff_time//3660), int(diff_time%3600//60), diff_time%3600%60)
          sentence = indent_str + '[{0}] : [start {1}] :'.format(dir_name,start_time)\
                              + colors('RED') \
                              + ' [now  number-{0} ({0}/{1}) {2} past]'.format(ongoing_number,len(iterate_pair),diff_time)\
                              + colors('END')
        sentence += '\n' + indent_str + '  [execute_file : {0}] [number of simulations : {1}] '.format(execute_file,len(iterate_pair)) 
        if(len(iterate_pair) > 0):
            sentence += '[change params :'
            for key in simulate_params:
                if(isinstance(simulate_params[key],list)):
                    sentence += ' ' +key + ','
        sentence += ']'
    else:
        sentence += indent_str + '[{}] : [not ready]'.format(dir_name) 
    print(sentence)


def plot_log(top_dir):
    print('[read whole parameter]')
    json_file = open(os.path.join(top_dir,'parameter.json'),'r')
    num_experiments = len(json.load(json_file)['experiments'])
    print('[number of experiments : {}]'.format(num_experiments))
    for i in range(num_experiments):
        experiment_dir = os.path.join(top_dir,'experiment_' + str(i+1))
        n_indent_experiment = 1
        time_log_print(experiment_dir,n_indent_experiment)


def log_check(top_dir):
    files_list = os.listdir(top_dir)
    experiment_dir_list  = [x for x in files_list if 'experiment' in x and os.path.isdir(os.path.join(top_dir, x))]
    date_dir_list  = [x for x in files_list if len(x.split('-')) > 5 and os.path.isdir(os.path.join(top_dir, x))]
    print('[top directory : {}]'.format(top_dir))
    if(len(experiment_dir_list) > 0):
        print('[top directory is root of experiments dir : plot all log in experiments]')
        plot_log(top_dir)
    elif(len(date_dir_list) > 0):
        print('[top directory is root of data : plot latest one]')
        date_dict = {}
        for dir in date_dir_list:
          date_dict[dir] =  datetime.strptime(dir,'%Y-%m-%d-%H-%M-%S') 
        latest_dir = max(date_dict)
        plot_log(os.path.join(top_dir,latest_dir))
    else:
      print('[Not root of results : lateset experiments plot : ref all "log_*.dat"]')
      files_list = glob.glob(top_dir + '*')
      for key in files_list:
          if('log' in key):
              log_file_name = key 
              color_print('[{0} : {1}]'.format(top_dir,log_file_name),'GREEN')
              if(os.path.exists(log_file_name)):
                  log_file = open(log_file_name,'r')
                  whole_lines = log_file.readlines()
                  length_lines = len(whole_lines)
                  parameter_declare = [x for x in whole_lines if 'parameter file' in x]
                  parameter_declare = parameter_declare[0].split('\n')[0]
                  print(parameter_declare)
                  target_dir_list = [x for x in whole_lines if 'set result output directory' in x] 
                  if(len(target_dir_list) == 1):
                      target_dir = target_dir_list[0].split(' ')[-1].split(']')[0]
                      target_dir = os.path.join(top_dir,target_dir)
                      if(os.path.isdir(target_dir)):
                          print('[result dir : {}]'.format(target_dir))
                          workstation = [x for x in whole_lines if 'server name' in x]
                          workstation = workstation[0].split('\n')[0]
                          print(workstation)
                          plot_log(target_dir)
                      else:
                          print('  [Error! no directory s.t : {}]'.format(target_dir))
              else:
                  print('  [Error! Not find particular sentence]') 
    print('[complete print]')


