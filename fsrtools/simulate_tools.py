import os
import json
import copy
import re
import shutil
import subprocess
import datetime
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


def operate_experiments(parameter_file=None, 
                        log_file=None, 
                        cout_tag=False, 
                        test_mode=False,
                        command_data=None,
                        structured_output=True,
                        ignore_abnormal_termination=False):

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

    if(ignore_abnormal_termination):
        log_write('[ignoreing abnormal termination mode]')

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
    log_write('[result directory : {}]'.format(json_data['experiment_dir']))
    setting_manager.set_directory(json_data['experiment_dir'])
    num_of_experiments = len(json_data['experiments'].keys())
    log_write('[number of experiment : {}]'.format(num_of_experiments))

    for key in json_data['experiments'].keys():
        num_of_simulate = len(json_data['experiments'][key]['simulate_params'].keys())
        log_write(' [{0} : number of simulate params: {1}]'.format(key,num_of_simulate)) 

    if(test_mode):
        for key in json_data['experiments'].keys():
            log_write('[{0}]'.format(key))
            for key_t in json_data['experiments'][key].keys():
                log_write(' [{0}]'.format(key_t))
                for key_tt in json_data['experiments'][key][key_t].keys():
                    parameter_value = json_data['experiments'][key][key_t][key_tt]
                    log_write('   {0} : {1}'.format(key_tt, parameter_value))

    if(structured_output):
        date_and_time = stop_watch.start_time(format='%Y-%m-%d-%H-%M-%S')
        experiment_directory = os.path.join(json_data['experiment_dir'], date_and_time + '/')
        log_write('[set result output directory : {}]'.format(experiment_directory))
        setting_manager.set_directory(experiment_directory)
    else:
        experiment_directory = json_data['experiment_dir']
        log_write('[structured output mode off : all results output in {} directly]'.format(experiment_directory))

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
                log_write('[Error ! : previous simulation does not exist !]')
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
        operate_simulations(json_data['experiments'][key],experiment_tag,log_write,command_data,
                            structured_output=structured_output,ignore_abnormal_termination=ignore_abnormal_termination)
        log_write.decrease_indent()
        log_write('[{0}][end experiment : {1} : lap time : {2}]'.format(key,stop_watch.lap_end(),stop_watch.lap_time()))
        previous_key = key

    log_write('[finish time : {}]'.format(stop_watch.end()))
    log_write('[duration : {}]'.format(stop_watch.duration()))
    json_data['time_info']['finish_time'] = stop_watch.end_time()
    json_data['time_info']['duration'] = stop_watch.duration()
    setting_manager.json_set(json_data, parameter_file_for_record)
    shutil.copy(log_file,os.path.join(experiment_directory,'log.dat'))


def operate_simulations(param_dict_original,experiment_tag,log_write,command_data,
                        structured_output=True,ignore_abnormal_termination=False):
    stop_watch = StopWatch()
    setting_manager = SettingManager(log_write) 

    param_dict = copy.deepcopy(param_dict_original)
    param_dict_original['experiment_params']['experiment_tag'] = experiment_tag 
    experiment_params = param_dict['experiment_params']
    simulate_params_original = param_dict['simulate_params']

    experiment_directory = experiment_params['experiment_dir']
    log_write('[check experiment directory : {}]'.format(experiment_directory))
    setting_manager.set_directory(experiment_directory)

    if(structured_output):
        simulate_directory = os.path.join(experiment_directory,experiment_tag + '/') 
        setting_manager.set_directory(simulate_directory)
    else:
        simulate_directory = experiment_directory 
    log_write('[simulate directory : {}]'.format(simulate_directory))
    experiment_params['experiment_dir'] = simulate_directory
    
    param_dict_original['time_info'] = {}
    param_dict_original['time_info']['start_time'] = stop_watch.start()
    parameter_file_simulation = os.path.join(simulate_directory,'parameter.json')
    setting_manager.json_set(param_dict_original,parameter_file_simulation)

    command_name = experiment_params['command_name']

    simulate_params_original, total_combinations = set_total_combinations(simulate_params_original,log_write)

    simulate_number = 1
    if(len(total_combinations) > 0):
        log_write('[total number of simulations : {}]'.format(len(total_combinations)))
        log_write('[check iterate lists]')
        log_write('[iterate combination list] : {}'.format(total_combinations))
    else:
        log_write('[total number of simulations : 1]')
        total_combinations.append(['NO_ITERATION'])

    for i in range(max(len(total_combinations),1)):
        if(len(total_combinations) > 1):
            simulate_params = set_simulate_params(simulate_params_original, total_combinations[i])
        else:
            simulate_params = simulate_params_original 
        log_write('[simulation : number-{}]'.format(simulate_number))
        log_write.add_indent()
        if(structured_output):
            result_directory = os.path.join(simulate_directory,'number-' + str(simulate_number) + '/')
            setting_manager.set_directory(result_directory)
        else:
            result_directory = simulate_directory
        execute_simulation(command_name,simulate_params,result_directory,log_write,command_data,
                           ignore_abnormal_termination=ignore_abnormal_termination)
        simulate_number += 1
        log_write.decrease_indent()

    param_dict_original['time_info']['end_time'] = stop_watch.end()
    param_dict_original['time_info']['duration'] = stop_watch.duration()
    setting_manager.json_set(param_dict_original,parameter_file_simulation)
    log_write('[all simulations complete]')


def execute_simulation(command_name,simulate_params,result_directory,log_write,
                       command_data,ignore_abnormal_termination=False): 
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
    log_write('[finish  : {}]'.format(stop_watch.end()))
    param_dict['time_info']['end_time'] = stop_watch.end_time()
    param_dict['time_info']['duration'] = stop_watch.duration()
    if(return_value != 0):
        param_dict['time_info']['remark'] = 'Abnormal termination : return_value : {}'.format(return_value)
        log_write('[Abnormal termination detected : return_value : {}]'.format(return_value))
        log_write.reset_indent()
        log_write('[Error End !]')
        setting_manager.json_set(param_dict,parameter_file_each_simulation)
        if(not ignore_abnormal_termination):
            raise ValueError('[Abnormal termination detected : return_value : {}]'.format(return_value))
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


def set_total_combinations(simulate_params,log_write):
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
                if(key_t != key and re.search( r'\b' + key_t+ r'\b',simulate_params[key])):
                    counter += 1
                    if(not isinstance(simulate_params[key_t], list) and not isinstance(simulate_params[key_t],str)):
                        local_variable_dict[key_t] = simulate_params[key_t]
            if(len(local_variable_dict) == counter):
                try:
                    calculated_value  = eval(simulate_params[key],globals(),local_variable_dict)
                    simulate_params_temp[key] = integer_filter(calculated_value)
                except NameError as err:
                    log_write('[{} as paremter : "{}" is input as "{}"]'.format(err,key,simulate_params[key]))
                    simulate_params_temp[key] = simulate_params[key]
                log_write('[{0} : {1}]'.format(key, simulate_params_temp[key]))
            else:
                for key_t in local_variable_dict.keys():
                    log_write('{0} is set at execute command set : depend on changing {1}'.format(key,key_t))

    total_combinations = product_combination_generator(iterate_dict)
    return simulate_params_temp,  total_combinations


def set_simulate_params(simulate_params,combination):
    for key in combination.keys():
        simulate_params[key] = combination[key]
    simulate_params_temp = copy.deepcopy(simulate_params)
    for key in simulate_params.keys():
        if(isinstance(simulate_params[key], str)):
            local_variable_dict = {}
            for key_t in simulate_params.keys():
                if(key_t != key and re.search( r'\b' + key_t+ r'\b',simulate_params[key])):
                    local_variable_dict[key_t] = simulate_params[key_t]
            try:
                calculated_value  = eval(simulate_params[key],globals(),local_variable_dict)
                simulate_params_temp[key] = integer_filter(calculated_value)
            except NameError as err:
                simulate_params_temp[key] = simulate_params[key]
    return simulate_params_temp


def integer_filter(n):
    if(isinstance(n, int)):
        return n
    elif(isinstance(n, float)):
        if(n.is_integer()):
            return int(n)
        else:
            return n
    else:
        return n




