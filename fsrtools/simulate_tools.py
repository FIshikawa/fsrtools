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

def operate_experiments(parameter_file=None, log_file=None, cout_tag=False, test_mode=False):
    current_directory = os.getcwd()

    if(test_mode):
        log_file = 'log_test.dat'
        parameter_file = 'parameter_test.json'
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

    experiment_directory = os.path.join(json_data['experiment_dir'], stop_watch.start_time.strftime('%Y-%m-%d-%H-%M-%S') + '/')
    log_write('[set result output directory : {}]'.format(experiment_directory))
    setting_manager.set_directory(experiment_directory)

    json_data['time_info'] = {}
    json_data['time_info']['start_time'] = start_time.strftime('%Y/%m/%d %H:%M:%S')
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
    json_data['time_info']['finish_time'] = stop_watch.end_time.strftime('%Y/%m/%d %H:%M:%S')
    json_data['time_info']['duration'] = stop_watch.duration.strftime('%d:%H:%M:%S')
    setting_manager.json_set(json_data, parameter_file_for_record)
    shutil.copy(log_file,os.path.join(experiment_directory,'log.dat'))


def operate_simulations(param_dict_original,experiment_tag,log_write):
    stop_watch = StopWatch()
    setting_manager = SettingManager(log_write) 

    param_dict = copy.deepcopy(param_dict_original)
    param_dict_original['experiment_params']['experiment_tag'] = experiment_tag 
    experiment_params = param_dict['experiment_params']
    simulate_params = param_dict['simulate_params']

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
    json_set(param_dict_original,parameter_file_simulation)

    command_name = experiment_params['command_name']

    simulate_params, iterate_dict , iterate_key_list, iterate_pair = set_simulate_params_iterate_dict(simulate_params,\
                                                                                                      command_name,\
                                                                                                      indent=nest_number,\
                                                                                                      log_file=log_file)

    simulate_number = 1
    if(len(iterate_dict.keys()) != 0):
        log_write('[check iterate lists]')
        log_write('[iterate_key_list] : {}'.format(iterate_key_list))
        log_write('[iterate_pair length : {}]'.format(len(iterate_pair)))
        log_write('[total number of simulations : {}]'.format(len(iterate_pair)))

        for i in range(len(iterate_pair)):
            simulate_params = set_simulate_params(simulate_params,iterate_key_list, iterate_pair[i], command_name)
            log_write('[simulation : number-{}]'.format(simulate_number))
            log_write.add_indent()
            result_directory = os.path.join(simulate_directory,'number-' + str(simulate_number) + '/')
            setting_manager.set_directory(result_directory)
            execute_simulation(command_name,simulate_params,result_directory,log_write)
            simulate_number += 1
            log_write.decrease_indent()
    else:
        log_write('[total number of simulations : 1]')
        log_write('[simulation : number-{}]'.format(simulate_number))
        log_write.add_indent()
        result_directory = os.path.join(simulate_directory,'number-' + str(simulate_number) + '/')
        setting_manager.set_directory(result_directory)
        execute_simulation(command_name,simulate_params,result_directory,log_write)
        simulate_number += 1
        log_write.decrease_indent()

    param_dict_original['time_info']['end_time'] = stop_watch.end()
    json_set(param_dict_original,parameter_file_simulation)
    log_write('[all simulations complete]')


def execute_simulation(command_name,simulate_params,result_directory,log_write): 
    stop_watch = StopWatch()
    setting_manager = SettingManager(log_write) 

    param_dict = {}
    param_dict['command_name'] = command_name
    param_dict['simulate_params'] = copy.deepcopy(simulate_params)
    param_dict['simulate_params']['result_directory'] = result_directory
    param_dict['time_info'] = {}
    param_dict['time_info']['start_time'] = stop_watch.start()
    execute_command = set_execute_command(command_name,param_dict['simulate_params'],log_write)
    if(len(execute_command) < 1):
        raise ValueError('the command_name can not be find in {}'.format(os.getcwd()))

    parameter_file_each_simulation = os.path.join(result_directory, 'parameter.json')
    setting_manager.json_set(param_dict,parameter_file_each_simulation)

    log_write('[execute : {}]'.format(stop_watch.start_time_str()))
    log_open = open(log_write.log_file,'a')
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
    param_dict['time_info']['end_time'] = stop_watch.end_time_str()
    setting_manager.json_set(param_dict,parameter_file_each_simulation)



def set_execute_command(command_name,simulate_params,log_write):
    execute_command = []
    commands_json = open(commands_json_file())
    commands_data = json.load(commands_json)
    if(command_name in commands_data.keys()):
        log_write('[detect : {}]'.format(command_name))
        command_list = commands_data[command_name]
    else:
        log_write('[can not find !]')

    for key in command_list:
        execute_command.append(simulate_params[key])
    log_write('[command_name line input]')
    log_write('{}'.format(execute_command))

    return execute_command


def product_combination_generator(iterate_dict):
    total_length = 1 
    length_dict = {}
    key_list = []
    total_combination = []
    if(len(iterate_dict.keys()) > 0):
        for key in iterate_dict.keys():
            length_dict[key] = len(iterate_dict[key])
            total_length = total_length * len(iterate_dict[key])
        total_combination = [[] for x in range(total_length)]
        previous_length = 1
        for key, value in sorted(length_dict.items(), key=lambda x: x[1]):
            key_list.append(key)
            for i in range(previous_length):
                for j in range(int(total_length/previous_length)):
                    total_combination[ j + i * int(total_length / previous_length)].append(iterate_dict[key][int(j // (float(total_length / previous_length) / float(value)))])
            previous_length = value

    return key_list, total_combination


def set_simulate_params_iterate_dict(simulate_params,command_name,indent=0,log_file=None):
    iterate_dict = {}
    logman = LogManager(indent=indent,log_file=log_file)
    for key in simulate_params.keys():
        if(isinstance(simulate_params[key], list)):
            iterate_dict[key] = simulate_params[key]
            logman.log_write('[detect : {0} : {1}]'.format(key, simulate_params[key]))
        elif(simulate_params[key] in ['Sweep','Power']):
            iterate_dict[key] = []
            logman.log_write('[detect : {0} : {1}]'.format(key, simulate_params[key]))
            logman.log_write('[number of iteration : {}]'.format(simulate_params['N_' + key]))
            if(simulate_params[key] == 'Sweep'):
                for i in range(simulate_params['N_' + key]):
                    iterate_dict[key].append(simulate_params[key+'_init'] + float(i) * simulate_params['d'+key])
            elif(simulate_params[key] == 'Power'):
                for i in range(simulate_params['N_' + key]):
                    iterate_dict[key].append(np.power(simulate_params[key+'_init'],float(i+1)))
                logman.log_write('{}'.format(iterate_dict[key]))

    if('clXYmodel' in command_name or 'clSpindemo' in command_name or 'fpu_thermalization' in command_name):
        if('N_thermalize' in simulate_params.keys()):
            if(simulate_params['N_thermalize'] == 'Auto'):
                logman.log_write('[detect : N_thermalize: Auto]')
                if(not isinstance(simulate_params['Ns'],str) and not isinstance(simulate_params['Ns'],list)): 
                    if(command_name.find('Cube') > 0):
                        simulate_params['N_thermalize'] =  simulate_params['Ns'] * simulate_params['Ns'] * simulate_params['Ns'] 
                    elif(command_name.find('Square') > 0):
                        simulate_params['N_thermalize'] =  simulate_params['Ns'] * simulate_params['Ns'] 
                    elif(command_name.find('Tesseract') > 0):
                        simulate_params['N_thermalize'] =  simulate_params['Ns'] * simulate_params['Ns'] * simulate_params['Ns'] * simulate_params['Ns'] 
                    else:
                        simulate_params['N_thermalize'] =  simulate_params['Ns'] 
                    logman.log_write('[N_thermalize : {}]'.format(simulate_params['N_thermalize']))
                elif(isinstance(simulate_params['Ns'],str) and isinstance(simulate_params['Ns'],list)): 
                    logman.log_write('[N_thermalize is set at simulation later]')

        if('Ns' in simulate_params.keys()):
            if(simulate_params['Ns'] == 'Auto'):
                logman.log_write('[detect : N_thermalize: Auto]')
                if(not isinstance(simulate_params['Ns'],str) and not isinstance(simulate_params['Ns'],list)): 
                    if(command_name.find('Cube') > 0):
                        simulate_params['Ns'] =  np.power(simulate_params['num_particles'],1/3)  
                    elif(command_name.find('Square') > 0):
                        simulate_params['Ns'] =  np.power(simulate_params['num_particles'],0.5)  
                    elif(command_name.find('Tesseract') > 0):
                        simulate_params['Ns'] =  np.power(simulate_params['num_particles'],1/4)  
                    else:
                        simulate_params['Ns'] =  simulate_params['num_particles']
                    logman.log_write('[Ns : {}]'.format(simulate_params['Ns']))
                elif(isinstance(simulate_params['Ns'],str) and isinstance(simulate_params['Ns'],list)): 
                    logman.log_write('[Ns is set at simulation later]')

        if('N_time' in simulate_params.keys()):
            if(simulate_params['N_time'] == 'Auto'):
                logman.log_write('[detect : N_time : Auto]')
                if(not isinstance(simulate_params['t'],str) and not isinstance(simulate_params['dt'],str)): 
                    if(not isinstance(simulate_params['t'],list) and not isinstance(simulate_params['dt'],list)): 
                        simulate_params['N_time'] =  int(simulate_params['t'] / simulate_params['dt'])
                        logman.log_write('[N_time : {}]'.format(simulate_params['N_time']))
            elif(isinstance(simulate_params['N_time'],str)):
                logman.log_write('[N_time is set at simulation later]')


    elif(command_name.find('MPO') > -1):
        if('N_time' in simulate_params.keys()):
            if(simulate_params['N_time'] == 'Auto'):
                logman.log_write('[detect : N_time : Auto]')
                if(not isinstance(simulate_params['t'],str) and not isinstance(simulate_params['dt'],str)): 
                    if(not isinstance(simulate_params['t'],list) and not isinstance(simulate_params['dt'],list)): 
                        simulate_params['N_time'] =  int(simulate_params['t'] / simulate_params['dt'])
                        logman.log_write('[N_time : {}]'.format(simulate_params['N_time']))
            elif(isinstance(simulate_params['N_time'],str)):
                logman.log_write('[N_time is set at simulation later]')

        if('D' in simulate_params.keys()):
            if(simulate_params['D'] == 'Auto'):
                logman.log_write('[detect : {} : Auto]'.format('D'))
                if(not isinstance(simulate_params['N'],str)):
                    simulate_params['D'] = simulate_params['N'] * 2
                    logman.log_write('[D : {1}]'.format(key, simulate_params['D']))
                elif(isinstance(simulate_params['N'],str)):
                    logman.log_write('[N will be set specially: set later]')

        if('tagged' in simulate_params.keys()):
            if(simulate_params['tagged'] == 'Auto'):
                logman.log_write('[detect : {} : Auto]'.format('tagged'))
                if(not isinstance(simulate_params['N'],str)):
                    if(not isinstance(simulate_params['N'],list)): 
                     simulate_params['tagged'] = simulate_params['N'] // 2
                    logman.log_write('[tagged : {1}]'.format(key, simulate_params['tagged']))
                elif(isinstance(simulate_params['N'],str)):
                    logman.log_write('[N will be set specially: set later]')

    iterate_list, total_combination = product_combination_generator(iterate_dict)
    return simulate_params, iterate_dict, iterate_list, total_combination


def set_simulate_params(simulate_params,iterate_key_list,iterate_pair,command_name):
    for i in range(len(iterate_key_list)):
        simulate_params[iterate_key_list[i]] = iterate_pair[i]

        if('clXYmodel' in command_name or 'clSpindemo' in command_name or 'fpu_thermalization' in command_name):
            if( iterate_key_list[i] in ['Ns']):
                if(command_name.find('Cube') > -1):
                    simulate_params['N_thermalize'] =  simulate_params['Ns'] * simulate_params['Ns'] * simulate_params['Ns'] 
                elif(command_name.find('Square') > 0):
                    simulate_params['N_thermalize'] =  simulate_params['Ns'] * simulate_params['Ns'] 
                elif(command_name.find('Tesseract') > 0):
                    simulate_params['N_thermalize'] =  simulate_params['Ns'] * simulate_params['Ns'] * simulate_params['Ns'] * simulate_params['Ns']
                else:
                    simulate_params['N_thermalize'] =  simulate_params['Ns']
                simulate_params['N_thermalize'] = int(simulate_params['N_thermalize']) 
            if( iterate_key_list[i] in ['num_particles']):
                if(command_name.find('Cube') > 0):
                    simulate_params['Ns'] =  np.power(simulate_params['num_particles'],1/3)  
                elif(command_name.find('Square') > 0):
                    simulate_params['Ns'] =  np.power(simulate_params['num_particles'],0.5)  
                elif(command_name.find('Tesseract') > 0):
                    simulate_params['Ns'] =  np.power(simulate_params['num_particles'],1/4)  
                else:
                    simulate_params['Ns'] =  simulate_params['num_particles']
                simulate_params['Ns'] =  int(simulate_params['Ns'])
            if( iterate_key_list[i] in ['t','dt']):
                simulate_params['N_time'] =  int(simulate_params['t'] / simulate_params['dt'])


        elif(command_name.find('MPO') > -1):
            if(iterate_key_list[i] == 'N'):
                simulate_params[iterate_key_list[i]] = int(iterate_pair[i])
                simulate_params['tagged'] = int(iterate_pair[i]) // 2
                simulate_params['D'] = int(iterate_pair[i]) * 2
            if( iterate_key_list[i] in ['t','dt']):
                simulate_params['N_time'] =  int(simulate_params['t'] / simulate_params['dt'])

    return simulate_params

def commands_json_file():
    return os.path.join(fsrtools.__path__[0],'config/commands.json')


class CommandManager:
    def __init__(self):
        self.__json_path = commands_json_file()
        commands_json = open(self.__json_path)
        self.commands_data = json.load(commands_json)
        self.commands_name_list = list(self.commands_data.keys())
        self.commands_list()

    def commands_list(self):
        for i in range(len(self.commands_name_list)):
            command_name = self.commands_name_list[i]
            print('[{0}] command name : {1} '.format(i,command_name))
            print('  {}'.format(self.commands_data[command_name]))

    def command(self,command_id):
        if(isinstance(command_id,int)):
            return self.commands_data[self.commands_name_list[command_id]]
        elif(isinstance(command_id, str)):
            return self.commands_data[command_id]
        else:
            raise ValueError('input is string or int')


    def add_command(self,command_dict):
        for key in command_dict.keys():
            if key in self.commands_data.keys():
                color_print('Error : command "{0}" is already registered'.format(key),'RED')
            else:
                print('add command "{0}"'.format(key))
                print(command_dict)
                self.commands_data[key] = commands_dict[key]

    def remove_command(self,command_name):
        if command_name in self.commands_data.keys():
            print('command {0} is removed'.format(command_name))
            del self.commands_data[command_name]
        else:
            color_print('Error : command {0} is not registered'.format(command_name),'RED')

    def save(self):
        f = open(self.__json_path,'w')
        json.dump(self.commands_data,f,indent=4)
        f.close()

    def test_simulate(self,command_id,execute_part):
        if(isinstance(command_id,int)):
            command_name =  self.commands_name_list[command_id]
        if(not command_name in self.commands_name_list):
            raise ValueError('not find {} in registered commands'.format(command_name))
        if(not execute_part in self.commands_data[command_name]):
            raise ValueError('{0} is not execute file part in {1}'.format(execute_part,command_name))
        print('test simulate : {}'.format(command_name))
        result_directory = './test_fsrsimulate/'
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
        for key in self.commands_data[command_name]:
            if(key == 'result_directory'):
                simulate_params[key] = result_directory
            elif(key == execute_part):
                simulate_params[execute_part] = execute_part
            else:
                simulate_params[key] = '1'
        execute_simulation(command_name,simulate_params,result_directory,log_write)
        print('test simulate end')


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
                                                                                                       indent=n_indent)
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


