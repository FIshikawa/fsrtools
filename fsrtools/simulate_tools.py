import os
import json
import copy
import shutil
import subprocess
from fsrtools.util import StopWatch
from fsrtools.util import SetDirectory
from fsrtools.util import LogManager
from fsrtools._paramset import set_simulate_params_iterate_dict
from fsrtools._paramset import set_simulate_params

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
    set_directory(experiment_directory)

    simulate_directory = os.path.join(experiment_directory,experiment_tag + '/') 
    log_write('[simulate directory : {}]'.format(simulate_directory))
    set_directory(simulate_directory)
    experiment_params['experiment_dir'] = simulate_directory
    
    param_dict_original['time_info'] = {}
    param_dict_original['time_info']['start_time'] = stop_watch.start()
    parameter_file_simulation = os.path.join(simulate_directory,'parameter.json')
    json_set(param_dict_original,parameter_file_simulation)

    execute_file = experiment_params['execute_file']

    simulate_params, iterate_dict , iterate_key_list, iterate_pair = set_simulate_params_iterate_dict(simulate_params,\
                                                                                                      execute_file,\
                                                                                                      indent=nest_number,\
                                                                                                      log_file=log_file)

    simulate_number = 1
    if(len(iterate_dict.keys()) != 0):
        log_write('[check iterate lists]')
        log_write('[iterate_key_list] : {}'.format(iterate_key_list))
        log_write('[iterate_pair length : {}]'.format(len(iterate_pair)))
        log_write('[total number of simulations : {}]'.format(len(iterate_pair)))

        for i in range(len(iterate_pair)):
            simulate_params = set_simulate_params(simulate_params,iterate_key_list, iterate_pair[i], execute_file)
            log_write('[simulation : number-{}]'.format(simulate_number))
            log_write.add_indent()
            simulate_number = execute_simulation(execute_file,simulate_params,simulate_number,simulate_directory,log_write)
            log_write.decrease_indent()
    else:
        log_write('[total number of simulations : 1]')
        log_write('[simulation : number-{}]'.format(simulate_number))
        log_write.add_indent()
        simulate_number = execute_simulation(execute_file,simulate_params,simulate_number,simulate_directory,log_write)
        log_write.decrease_indent()

    param_dict_original['time_info']['end_time'] = stop_watch.end()
    json_set(param_dict_original,parameter_file_simulation)
    log_write('[all simulations complete]')


def execute_simulation(execute_file,simulate_params,simulate_number,simulate_directory,log_write): 
    stop_watch = StopWatch()
    setting_manager = SettingManager(log_write) 

    result_directory = os.path.join(simulate_directory,'number-' + str(simulate_number) + '/')
    setting_manager.set_directory(result_directory)
    execute_command = set_execute_command(execute_file,result_directory,simulate_params)
    if(len(execute_command) < 1):
        raise ValueError('the execute_file can not be find in {}'.format(os.getcwd()))
    param_dict = {}
    param_dict['simulate_params'] = copy.deepcopy(simulate_params)
    param_dict['result_dir'] = result_directory
    param_dict['execute_file'] = execute_file
    param_dict['time_info'] = {}
    param_dict['time_info']['start_time'] = stop_watch.start()

    parameter_file_each_simulation = os.path.join(result_directory, 'parameter.json')
    setting_manager.json_set(param_dict,parameter_file_each_simulation)

    log_write('[execute : {}]'.format(stop_watch.start_time.strftime('%Y/%m/%d %H:%M:%S')))
    p = subprocess.Popen(execute_command,stdout=log_open,stderr=log_open)
    p.wait()
    return_value = p.wait()
    if(return_value != 0):
        log_write('[Abnormal termination detected : return_value : {}]'.format(return_value))
        reset_indent()
        log_write('[Error End !]')
        raise ValueError('[Abnormal termination detected : return_value : {}]'.format(return_value))

    log_write('[finish  : {}]'.format(stop_watch.end()))
    param_dict['time_info']['end_time'] = stop_watch.end_time.strftime('%Y/%m/%d %H:%M:%S')
    json_set(param_dict,parameter_file_each_simulation)

    simulate_number += 1
    return simulate_number


def set_execute_command(execute_file,result_directory,param_dict):
    execute_command = []

    if(execute_file.find('fpu_thermalization') > -1):
        log_write('[detect : {}]'.format(execute_file))
        files_list = os.listdir(os.getcwd())
        if(not execute_file in files_list):
            log_write('[Error ! : can not find execute_file!]')
        else:
            execute_file = './' + execute_file 
            execute_command.append(execute_file) 
            execute_command.append(result_directory)
            execute_command.append(str(int(param_dict['Ns']))) 
            execute_command.append(str(int(param_dict['N_time']))) 
            execute_command.append(str(param_dict['t']))
            execute_command.append(str(param_dict['alpha']))
            execute_command.append(str(param_dict['beta']))
            execute_command.append(str(param_dict['E_initial']))
            execute_command.append(str(int(param_dict['N_normalmode']))) 
            execute_command.append(str(int(param_dict['n_bin'])))
            execute_command.append(str(int(param_dict['N_loop']))) 
            execute_command.append(str(int(param_dict['N_parallel']))) 
            execute_command.append(str(int(param_dict['N_time_resolve']))) 
            log_file = log_file
            log_open = open(log_file,'a')
            log_write('[command line input]')
            log_write('{}'.format(execute_command))


    elif(execute_file.find('clXYmodelNonEq') > -1):
        log_write('[detect : {}]'.format(execute_file))
        files_list = os.listdir(os.getcwd())
        if(not execute_file in files_list):
            log_write('[Error ! : can not find execute_file!]')
        else:
            execute_file = './' + execute_file 
            execute_command.append(execute_file) 
            execute_command.append(result_directory)
            execute_command.append(str(int(param_dict['N_thermalize']))) 
            execute_command.append(str(int(param_dict['Ns']))) 
            execute_command.append(str(param_dict['T']))
            execute_command.append(str(int(param_dict['N_time']))) 
            execute_command.append(str(param_dict['t']))
            execute_command.append(str(int(param_dict['n_bin'])))
            execute_command.append(str(int(param_dict['N_loop']))) 
            execute_command.append(str(int(param_dict['N_parallel']))) 
            execute_command.append(str(int(param_dict['N_time_resolve']))) 
            execute_command.append(str(int(param_dict['Ns_observe']))) 
            execute_command.append(str(param_dict['D'])) 
            execute_command.append(str(param_dict['Inte'])) 
            execute_command.append(str(param_dict['Freq'])) 
            log_file = log_file
            log_open = open(log_file,'a')
            log_write('[command line input]')
            log_write('{}'.format(execute_command))

    elif(execute_file.find('clSpindemo') > -1 ):
        log_write('[detect : {}]'.format(execute_file))
        files_list = os.listdir(os.getcwd())
        if(not execute_file in files_list):
            log_write('[Error ! : can not find execute_file!]')
        else:
            execute_file = './' + execute_file 
            execute_command.append(execute_file) 
            execute_command.append(result_directory)
            execute_command.append(str(int(param_dict['N_thermalize']))) 
            execute_command.append(str(int(param_dict['Ns']))) 
            execute_command.append(str(param_dict['T']))
            execute_command.append(str(int(param_dict['N_time']))) 
            execute_command.append(str(param_dict['t']))
            execute_command.append(str(int(param_dict['N_relax']))) 
            execute_command.append(str(int(param_dict['Ns_observe']))) 
            log_file = log_file
            log_open = open(log_file,'a')
            log_write('[command line input]')
            log_write('{}'.format(execute_command))

    elif(execute_file.find('clXYmodelCriticalMD') > -1 ):
        log_write('[detect : {}]'.format(execute_file))
        files_list = os.listdir(os.getcwd())
        if(not execute_file in files_list):
            log_write('[Error ! : can not find execute_file!]')
        else:
            execute_file = './' + execute_file 
            execute_command.append(execute_file) 
            execute_command.append(result_directory)
            execute_command.append(str(int(param_dict['N_thermalize']))) 
            execute_command.append(str(int(param_dict['Ns']))) 
            execute_command.append(str(param_dict['T']))
            execute_command.append(str(param_dict['d_T'])) 
            execute_command.append(str(int(param_dict['N_T']))) 
            execute_command.append(str(int(param_dict['N_loop']))) 
            execute_command.append(str(int(param_dict['N_time']))) 
            execute_command.append(str(param_dict['t']))
            execute_command.append(str(int(param_dict['N_parallel']))) 
            execute_command.append(str(int(param_dict['Ns_observe']))) 
            execute_command.append(str(int(param_dict['n_bin']))) 
            log_file = log_file
            log_open = open(log_file,'a')
            log_write('[command line input]')
            log_write('{}'.format(execute_command))

    elif(execute_file.find('clXYmodelCritical') > -1 ):
        log_write('[detect : {}]'.format(execute_file))
        files_list = os.listdir(os.getcwd())
        if(not execute_file in files_list):
            log_write('[Error ! : can not find execute_file!]')
        else:
            execute_file = './' + execute_file 
            execute_command.append(execute_file) 
            execute_command.append(result_directory)
            execute_command.append(str(int(param_dict['N_thermalize']))) 
            execute_command.append(str(int(param_dict['Ns']))) 
            execute_command.append(str(param_dict['T']))
            execute_command.append(str(param_dict['d_T'])) 
            execute_command.append(str(int(param_dict['N_T']))) 
            execute_command.append(str(int(param_dict['N_loop']))) 
            execute_command.append(str(int(param_dict['N_relax']))) 
            execute_command.append(str(int(param_dict['N_parallel']))) 
            execute_command.append(str(int(param_dict['Ns_observe']))) 
            execute_command.append(str(int(param_dict['n_bin']))) 
            log_file = log_file
            log_open = open(log_file,'a')
            log_write('[command line input]')
            log_write('{}'.format(execute_command))

    elif(execute_file.find('clXYmodelWangLandau') > -1):
        log_write('[detect : {}]'.format(execute_file))
        files_list = os.listdir(os.getcwd())
        if(not execute_file in files_list):
            log_write('[Error ! : can not find execute_file!]')
        else:
            execute_file = './' + execute_file 
            execute_command.append(execute_file) 
            execute_command.append(result_directory)
            execute_command.append(str(int(param_dict['Ns'])))
            execute_command.append(str(param_dict['bin']))
            execute_command.append(str(param_dict['E_max']))
            execute_command.append(str(param_dict['E_min']))
            execute_command.append(str(int(param_dict['max_iteration']))) 
            log_file = log_file
            log_open = open(log_file,'a')
            log_write('[command line input]')
            log_write('{}'.format(execute_command))

    elif(execute_file.find('clXYmodel') > -1):
      log_write('[detect : {}]'.format(execute_file))
      files_list = os.listdir(os.getcwd())
      if(not execute_file in files_list):
        log_write('[Error ! : can not find execute_file!]')
      else:
        execute_file = './' + execute_file 
        execute_command.append(execute_file) 
        execute_command.append(result_directory)
        execute_command.append(str(int(param_dict['N_thermalize']))) 
        execute_command.append(str(int(param_dict['Ns']))) 
        execute_command.append(str(param_dict['T']))
        execute_command.append(str(int(param_dict['N_time']))) 
        execute_command.append(str(param_dict['t']))
        execute_command.append(str(int(param_dict['n_bin'])))
        execute_command.append(str(int(param_dict['N_loop']))) 
        execute_command.append(str(int(param_dict['N_parallel']))) 
        execute_command.append(str(int(param_dict['N_time_resolve']))) 
        execute_command.append(str(int(param_dict['Ns_observe']))) 
        log_file = log_file
        log_open = open(log_file,'a')
        log_write('[command line input]')
        log_write('{}'.format(execute_command))

    elif(execute_file.find('MPO') > -1):
        log_write('[detect : {}]'.format('MPO'))
        files_list = os.listdir(os.getcwd())
        if(not execute_file in files_list):
            log_write('[Error ! : can not find execute_file!]')
        else:
            execute_command.append('python') 
            execute_command.append(execute_file) 
            execute_command.append(result_directory)
            execute_command.append(str(int(param_dict['N']))) 
            execute_command.append(str(int(param_dict['D']))) 
            execute_command.append(str(param_dict['J']))
            execute_command.append(str(param_dict['h']))
            execute_command.append(str(param_dict['V']))
            execute_command.append(str(param_dict['coef']))
            execute_command.append(str(param_dict['t']))
            execute_command.append(str(int(param_dict['N_time'])))
            execute_command.append(str(param_dict['T']))
            execute_command.append(str(int(param_dict['tagged'])))
            execute_command.append(str(param_dict['test_mode']))
            log_file = log_file
            log_open = open(log_file,'a')
            log_write('[command line input]')
            log_write('{}'.format(execute_command))

    else:
        log_write('[can not find !]')

    return execute_command

