import os
import datetime
import json
from fsrtools.utils import *
from fsrtools.utils.colors import *

def log_check(target):
    if os.path.exists(target) and not os.path.isdir(target):
        print('[input log file : {}]'.format(target))
        _log_check(target)
    elif os.path.isdir(target):
        top_directory = target
        elements_list = os.listdir(top_directory)
        date_dir_list = []
        experiment_dir_list = []
        for element in elements_list:
            if 'experiment' in element and \
                        os.path.isdir(os.path.join(top_directory, element)):
                experiment_dir_list.append(element)

            if len(element.split('-')) > 5 and \
                        os.path.isdir(os.path.join(top_directory, element)):
                date_dir_list.append(element)
        print('[top directory : {}]'.format(top_directory))

        if len(experiment_dir_list):
            print('[top is root of experiments : plot all log]')
            plot_log(top_directory)
        elif len(date_dir_list):
            print('[top directory is root of data]')
            for target_directory in date_dir_list:
                color_print('[{0}]'.format(target_directory),'GREEN')
                plot_log(os.path.join(top_directory,target_directory))
        else:
          print('[Not root of results : all "log*.dat"]')
          for element in elements_list:
              if 'log' in element and 'dat' in element:
                    log_file_name = element
                    color_print('[{0} : {1}]'
                            .format(top_directory,log_file_name),'GREEN')
                    log_file_path = \
                                os.path.join(top_directory,log_file_name)
                    _log_check(log_file_path)
        print('[complete print]')


def _log_check(log_file_path):
    log_file = open(log_file_path,'r')
    whole_lines = log_file.readlines()
    length_lines = len(whole_lines)
    parameter_declare = [x for x in whole_lines if 'parameter file' in x]
    parameter_declare = parameter_declare[0].split('\n')[0]
    print(parameter_declare)
    target_dir_list = [x for x in whole_lines \
                            if 'set result output directory' in x] 

    if len(target_dir_list) == 1:
        target_directory = target_dir_list[0].split(' ')[-1].split(']')[0]
        current_directory_path = os.getcwd()
        target_directory = \
            os.path.join(current_directory_path, target_directory)

        if os.path.isdir(target_directory):
            print('[result directory : {}]'.format(target_directory))
            workstation = [x for x in whole_lines if 'server name' in x]
            workstation = workstation[0].split('\n')[0]
            print(workstation)
            plot_log(target_directory)
        else:
            print('  [Error! {} des not exist]'.format(target_directory))
    else:
        print('[Error! {} has no expected form]'.format(log_file_path))


def plot_log(target_directory):
    json_file = open(os.path.join(target_directory,'parameter.json'),'r')
    num_experiments = len(json.load(json_file)['experiments'])
    print('[number of experiments : {}]'.format(num_experiments))
    for i in range(num_experiments):
        experiment_directory = \
            os.path.join(target_directory,'experiment_' + str(i+1))
        time_log_print(experiment_directory,n_indent=1)
        if os.path.exists(experiment_directory):
            ongoing_directories = \
                sorted([x for x in os.listdir(experiment_directory) \
                    if os.path.isdir(os.path.join(experiment_directory,x))])
            for directory in ongoing_directories:
                ongoing_directory = \
                            os.path.join(experiment_directory,directory)
                time_log_print(ongoing_directory,n_indent=3)


def time_log_print(directory_path,n_indent=1):
    log_write = LogManager(n_indent=n_indent,cout_tag=True)
    directory_name = os.path.basename(os.path.normpath(directory_path))
    if os.path.exists(directory_path):
        json_file = open(os.path.join(directory_path,'parameter.json'),'r')
        json_data = json.load(json_file)
        time_info = json_data['time_info']
        sentence = ''
        ongoing_number = \
                 len([x for x in os.listdir(directory_path) \
                      if 'number' in x and \
                            os.path.isdir(os.path.join(directory_path,x))])

        if 'start_time' in time_info.keys() and \
                                    len(time_info['start_time']) > 0:
            start_time = time_info['start_time']
        else:
            start_time = 'wating'

        if 'end_time' in time_info.keys() and \
                                    len(time_info['end_time']) > 0:

            end_time = time_info['end_time']
            duration_time = time_info['duration']
        else:
            nowtime = datetime.datetime.now()
            duration_time =  nowtime \
                              - datetime.datetime.strptime(start_time, 
                                                        '%Y/%m/%d %H:%M:%S')
            end_time = None

        if ongoing_number:
            simulate_params = json_data['simulate_params']
            command_name = \
                        json_data['experiment_params']['command_name']
            print_temp = lambda sentence : sentence
            simulate_params, total_combinations = \
                    set_total_combinations(simulate_params,print_temp)

            if end_time is None:
                sentence = '[{0}] : [start {1}] : [past {2}] : ' \
                               .format(directory_name,start_time,duration_time)
                sentence += '[ongoing  number-{0} ({0}/{1})]'\
                            .format(ongoing_number,len(total_combinations))
            else:
                sentence = '[{0}] : [start {1}] : [end {2}] : [duration {3}]'\
                      .format(directory_name,start_time,end_time,duration_time)
                sentence += ' : [completed ({0}/{1})]'\
                            .format(ongoing_number,len(total_combinations))
            log_write(sentence)

            sentence = '  [command_name : {0}] ' \
                   .format(command_name,max(len(total_combinations),1)) 

            if len(total_combinations):
                sentence += '[change params :'
                for key in simulate_params:
                    if isinstance(simulate_params[key],list):
                        sentence += ' ' +key + ','
                sentence += ']'

            log_write(sentence)

        else:
            if end_time is not None:
                sentence = '[{0}] : [start {1}] : [end {2}] : [duration {3}] '\
                      .format(directory_name,start_time,end_time,duration_time)
            else:
                sentence = '[{0}] : [start {1}] :' \
                                .format(directory_name,start_time) \
                                + colors('RED') \
                                + ' [past {}] '.format(str(duration_time))\
                                + colors('END')

            if 'remark' in time_info.keys():
                sentence += colors('RED') + '[{}] ' \
                                .format(time_info['remark']) + colors('END')

            log_write(sentence)
    else:
        log_write('[{}] : [yet execute]'.format(directory_name))

