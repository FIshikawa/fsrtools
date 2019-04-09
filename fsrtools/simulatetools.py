import numpy as np
import math
import datetime
import sys
import os
import json
import copy
import shutil
import subprocess
from paramset import set_simulate_params_iterate_dict
from paramset import set_simulate_params


class ExperimentManager:
    def __init__(self, parameter_file=None, log_file=None, cout=False, test_mode=False):
        if(test_mode):
            self.__log_file_name = 'log_test.dat'
            self.__parameter_file = 'parameter_test.json'
        else:
            self.__log_file_name = log_file
            self.__parameter_file = parameter_file
        current_dir = os.getcwd()
        self.__log_file_name = os.path.join(current_dir, self.__log_file_name)
        if(test_mode):
            self.__cout = True
        else:
            self.__cout = cout  
        self.__experiment_tag = ''
        self.__top_directory = ''
        self.__nest_number = 0
        self.__test_mode = test_mode
        json_file = open(self.__parameter_file,'r')
        self.__json_data = json.load(json_file)
  
        if(os.path.exists(self.__log_file_name)):
            os.remove(self.__log_file_name) 
  
        start_time =  datetime.datetime.now() 
        self.__log_write('[start time : {}]'.format(start_time.strftime('%Y/%m/%d %H:%M:%S')))
        if(test_mode):
            self.__log_write('[test mode]')
        self.__log_write('[set log file at : {}]'.format(self.__log_file_name))
  
        server_name = '%s' % os.uname()[1]
        self.__log_write('[server name : {}]'.format(server_name))
        if(self.__parameter_file == None):
            self.__log_write('Error! : not select json files')
            sys.exit()
        else:
            self.__log_write('[parameter file : {}]'.format(self.__parameter_file))  
        if(self.__test_mode):
            if(self.__json_data['experiment_dir'] != 'test/'): 
                self.__log_write('[experiment_dir is not "test/" : dir should be it]')
                self.__json_data['experiment_dir'] = 'test/'
  
        current_dir = os.getcwd()
        current_dir_name = os.path.dirname(current_dir)
        if(self.__test_mode):
            self.__log_write('[current_dir list : {}]'.format(current_dir_name))
        if(current_dir_name != 'build'):
            dir_list = os.listdir(current_dir) 
            if('build' in dir_list):
                os.chdir('./build')
                self.__log_write('[move to build directory]')
            else:
                self.__log_write('[not find build dir]')
  
        self.__log_write('[paramter data info]')
        self.__log_write('[result dir : {}]'.format(self.__json_data['experiment_dir']))
        self.__set_directory(self.__json_data['experiment_dir'])
        self.__log_write('[number of experiment : {}]'.format(len(self.__json_data['experiments'].keys())))
        for key in self.__json_data['experiments'].keys():
            self.__log_write(' [{0} : number of simulate params: {1}]'.format(key, len(self.__json_data['experiments'][key]['simulate_params'].keys())))
  
        if(self.__test_mode):
            for key in self.__json_data['experiments'].keys():
                self.__log_write('[{0}]'.format(key))
                for key_t in self.__json_data['experiments'][key].keys():
                    self.__log_write(' [{0}]'.format(key_t))
                    for key_tt in self.__json_data['experiments'][key][key_t].keys():
                        self.__log_write('   {0} : {1}'.format(key_tt, self.__json_data['experiments'][key][key_t][key_tt]))


    def operate_experiments(self):
        start_time =  datetime.datetime.now() 
        result_dir_name = self.__json_data['experiment_dir'] + start_time.strftime('%Y-%m-%d-%H-%M-%S') + '/'
        self.__log_write('[set result output directory : {}]'.format(result_dir_name))
        self.__set_directory(result_dir_name)
        self.__set_top_directory(result_dir_name)
        self.__json_data['time_info'] = {}
        self.__json_data['time_info']['start_time'] = start_time.strftime('%Y/%m/%d %H:%M:%S')
        self.__json_set(self.__json_data, result_dir_name + 'parameter.json')
        previous_key = ''
        for key in self.__json_data['experiments'].keys():
            start_time =  datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            self.__log_write('[{0}][start experiment : {1}]'.format(key,start_time))
            self.__add_indent()
            self.__set_experiment_tag(key)
            if('Same' in self.__json_data['experiments'][key]['simulate_params'].keys()):
                if(len(previous_key) < 1):
                    print('[Error ! : previous simulation does not exist !]')
                key_list_temp = self.__json_data['experiments'][key]['simulate_params'].keys()
                key_list_temp.remove('Same')
                value_dict_temp = {}
                for key_temp in key_list_temp:
                    value_dict_temp[key_temp] = self.__json_data['experiments'][key]['simulate_params'][key_temp]
                self.__json_data['experiments'][key]['simulate_params'] = copy.deepcopy(self.__json_data['experiments'][previous_key]['simulate_params'])
                for key_temp in key_list_temp:
                    self.__json_data['experiments'][key]['simulate_params'][key_temp] = value_dict_temp[key_temp] 
            self.__json_data['experiments'][key]['experiment_params']['experiment_dir'] = result_dir_name
            self.__execute_experiment(self.__json_data['experiments'][key])
            end_time =  datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            self.__decrease_indent()
            self.__log_write('[{0}][end experiment : {1}]'.format(key,end_time))
            previous_key = key
  
        self.__init_experiment_tag()
        finish_time =  datetime.datetime.now() 
        self.__json_data['time_info']['finish_time'] = finish_time.strftime('%Y/%m/%d %H:%M:%S')
        self.__json_set(self.__json_data, result_dir_name + 'parameter.json')
        self.__log_write('[finish time : {}]'.format(finish_time.strftime('%Y/%m/%d %H:%M:%S')))
        self.__end_log_copy()

    def __execute_experiment(self,param_dict_original):
        # execute experiment according to operate parameter
        param_dict = copy.deepcopy(param_dict_original)
        param_dict_original['experiment_params']['experiment_tag'] = self.experiment_tag 
        experiment_params = param_dict['experiment_params']
        simulate_params = param_dict['simulate_params']
    
        experiment_dir_name = experiment_params['experiment_dir']
        self.__log_write('[check experiment directory : {}]'.format(experiment_dir_name))
        self.__set_directory(experiment_dir_name)
  
        simulate_dir_name = experiment_dir_name + self.experiment_tag + '/' 
        self.__log_write('[simulate directory : {}]'.format(simulate_dir_name))
        self.__set_directory(simulate_dir_name)
        experiment_params['experiment_dir'] = simulate_dir_name
        
        param_dict_original['time_info'] = {}
        param_dict_original['time_info']['start_time'] = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        json_log_file_name = simulate_dir_name + 'parameter.json'
        self.__json_set(param_dict_original,json_log_file_name)
  
        execute_file = experiment_params['execute_file']
  
        simulate_params, iterate_dict , iterate_key_list, iterate_pair = set_simulate_params_iterate_dict(simulate_params,\
                                                                                                          execute_file,\
                                                                                                          indent=self.__nest_number,\
                                                                                                          log_file=self.__log_file_name)
  
        simulate_number = 1
        if(len(iterate_dict.keys()) != 0):
            self.__log_write('[check iterate lists]')
            self.__log_write('[iterate_key_list] : {}'.format(iterate_key_list))
            self.__log_write('[iterate_pair length : {}]'.format(len(iterate_pair)))
            self.__log_write('[total number of simulations : {}]'.format(len(iterate_pair)))
  
            for i in range(len(iterate_pair)):
                simulate_params = set_simulate_params(simulate_params,iterate_key_list, iterate_pair[i], execute_file)
                self.__log_write('[simulation : number-{}]'.format(simulate_number))
                self.__add_indent()
                simulate_number = self.__operate_simulation(execute_file,simulate_params,simulate_number,simulate_dir_name)
                self.__decrease_indent()
        else:
            self.__log_write('[total number of simulations : 1]')
            self.__log_write('[simulation : number-{}]'.format(simulate_number))
            self.__add_indent()
            simulate_number = self.__operate_simulation(execute_file,simulate_params,simulate_number,simulate_dir_name)
            self.__decrease_indent()
  
        end_time = datetime.datetime.now()
        param_dict_original['time_info']['end_time'] = end_time.strftime('%Y/%m/%d %H:%M:%S')
        json_log_file_name = simulate_dir_name + 'parameter.json'
        self.__json_set(param_dict_original,json_log_file_name)
        self.__log_write('[all simulations complete]')


    def __operate_simulation(self,execute_file,simulate_params,simulate_number,simulate_dir_name): 
        result_dir = simulate_dir_name + 'number-' + str(simulate_number) + '/'
        self.__set_directory(result_dir)
        param_dict = {}
        param_dict['simulate_params'] = copy.deepcopy(simulate_params)
        self.__execute_simulation(execute_file,result_dir,simulate_params)
        simulate_number += 1
        return simulate_number
  
    def __set_experiment_tag(self,experiment_tag,Add=False):
        if(Add):
          self.experiment_tag += experiment_tag
        else:
          self.experiment_tag = experiment_tag
  
    def __init_experiment_tag(self):
        self.experiment_tag = ''

    def __reset_indent(self):
        self.__nest_number = 0

    def __add_indent(self):
        self.__nest_number += 1

    def __decrease_indent(self):
        self.__nest_number -= 1

    def __set_indent_str(self):
        indent_str = ''
        for i in range(self.__nest_number):
            indent_str += '  ' 
        return indent_str

    def __json_set(self,parameter_dict,file_name):
        f = open(file_name,'w')
        json.dump(parameter_dict,f,indent=4)
        f.close()

    def __log_write(self,sentence,temp_log_file_name=None):
        if(temp_log_file_name==None):
            f = open(self.__log_file_name,"a")
        else:
            f = open(temp_log_file_name,"a")
        indent_str = self.__set_indent_str()
        sentence = indent_str + sentence
        f.write(sentence + '\n')
        f.close()
        if(self.__cout):
            print(sentence)

    def __set_directory(self,dir_name):
      if(os.path.exists(dir_name) != True):
        os.mkdir(dir_name)
        self.__log_write('[Create : {}]'.format(dir_name))
      else:
        self.__log_write('[Already exist]')

    def __set_top_directory(self, dir_name):
        self.__top_directory = dir_name

    def __end_log_copy(self):
        shutil.copy(self.__log_file_name,self.__top_directory + 'log.dat')
  
    def __execute_simulation(self,execute_file,result_dir,param_dict):
        operate_set = []
        info = True

        if(execute_file.find('clXYmodelNonEq') > -1):
            self.__log_write('[detect : {}]'.format(execute_file))
            files_list = os.listdir(os.getcwd())
            if(not execute_file in files_list):
                self.__log_write('[Error ! : can not find execute_file!]')
                info = False
            else:
                execute_file = './' + execute_file 
                operate_set.append(execute_file) 
                operate_set.append(result_dir)
                operate_set.append(str(int(param_dict['N_thermalize']))) 
                operate_set.append(str(int(param_dict['Ns']))) 
                operate_set.append(str(param_dict['T']))
                operate_set.append(str(int(param_dict['N_time']))) 
                operate_set.append(str(param_dict['t']))
                operate_set.append(str(int(param_dict['n_bin'])))
                operate_set.append(str(int(param_dict['N_loop']))) 
                operate_set.append(str(int(param_dict['N_parallel']))) 
                operate_set.append(str(int(param_dict['N_time_resolve']))) 
                operate_set.append(str(int(param_dict['Ns_observe']))) 
                operate_set.append(str(param_dict['D'])) 
                operate_set.append(str(param_dict['Inte'])) 
                operate_set.append(str(param_dict['Freq'])) 
                log_file_name = self.__log_file_name
                log_open = open(log_file_name,'a')
                self.__log_write('[command line input]')
                self.__log_write('{}'.format(operate_set))
  
        elif(execute_file.find('clSpindemo') > -1 ):
            self.__log_write('[detect : {}]'.format(execute_file))
            files_list = os.listdir(os.getcwd())
            if(not execute_file in files_list):
                self.__log_write('[Error ! : can not find execute_file!]')
                info = False
            else:
                execute_file = './' + execute_file 
                operate_set.append(execute_file) 
                operate_set.append(result_dir)
                operate_set.append(str(int(param_dict['N_thermalize']))) 
                operate_set.append(str(int(param_dict['Ns']))) 
                operate_set.append(str(param_dict['T']))
                operate_set.append(str(int(param_dict['N_time']))) 
                operate_set.append(str(param_dict['t']))
                operate_set.append(str(int(param_dict['N_relax']))) 
                operate_set.append(str(int(param_dict['Ns_observe']))) 
                log_file_name = self.__log_file_name
                log_open = open(log_file_name,'a')
                self.__log_write('[command line input]')
                self.__log_write('{}'.format(operate_set))
  
        elif(execute_file.find('clXYmodelCriticalMD') > -1 ):
            self.__log_write('[detect : {}]'.format(execute_file))
            files_list = os.listdir(os.getcwd())
            if(not execute_file in files_list):
                self.__log_write('[Error ! : can not find execute_file!]')
                info = False
            else:
                execute_file = './' + execute_file 
                operate_set.append(execute_file) 
                operate_set.append(result_dir)
                operate_set.append(str(int(param_dict['N_thermalize']))) 
                operate_set.append(str(int(param_dict['Ns']))) 
                operate_set.append(str(int(param_dict['N_time']))) 
                operate_set.append(str(param_dict['t']))
                operate_set.append(str(param_dict['T']))
                operate_set.append(str(param_dict['d_T'])) 
                operate_set.append(str(int(param_dict['N_T']))) 
                operate_set.append(str(int(param_dict['N_loop']))) 
                operate_set.append(str(int(param_dict['N_parallel']))) 
                operate_set.append(str(int(param_dict['Ns_observe']))) 
                operate_set.append(str(int(param_dict['n_bin']))) 
                log_file_name = self.__log_file_name
                log_open = open(log_file_name,'a')
                self.__log_write('[command line input]')
                self.__log_write('{}'.format(operate_set))
  
        elif(execute_file.find('clXYmodelCritical') > -1 ):
            self.__log_write('[detect : {}]'.format(execute_file))
            files_list = os.listdir(os.getcwd())
            if(not execute_file in files_list):
                self.__log_write('[Error ! : can not find execute_file!]')
                info = False
            else:
                execute_file = './' + execute_file 
                operate_set.append(execute_file) 
                operate_set.append(result_dir)
                operate_set.append(str(int(param_dict['N_thermalize']))) 
                operate_set.append(str(int(param_dict['Ns']))) 
                operate_set.append(str(param_dict['T']))
                operate_set.append(str(param_dict['d_T'])) 
                operate_set.append(str(int(param_dict['N_T']))) 
                operate_set.append(str(int(param_dict['N_loop']))) 
                operate_set.append(str(int(param_dict['N_relax']))) 
                operate_set.append(str(int(param_dict['N_parallel']))) 
                operate_set.append(str(int(param_dict['Ns_observe']))) 
                operate_set.append(str(int(param_dict['n_bin']))) 
                log_file_name = self.__log_file_name
                log_open = open(log_file_name,'a')
                self.__log_write('[command line input]')
                self.__log_write('{}'.format(operate_set))
  
        elif(execute_file.find('clXYmodelWangLandau') > -1):
            self.__log_write('[detect : {}]'.format(execute_file))
            files_list = os.listdir(os.getcwd())
            if(not execute_file in files_list):
                self.__log_write('[Error ! : can not find execute_file!]')
                info = False
            else:
                execute_file = './' + execute_file 
                operate_set.append(execute_file) 
                operate_set.append(result_dir)
                operate_set.append(str(int(param_dict['Ns'])))
                operate_set.append(str(param_dict['bin']))
                operate_set.append(str(param_dict['E_max']))
                operate_set.append(str(param_dict['E_min']))
                operate_set.append(str(int(param_dict['max_iteration']))) 
                log_file_name = self.__log_file_name
                log_open = open(log_file_name,'a')
                self.__log_write('[command line input]')
                self.__log_write('{}'.format(operate_set))
  
        elif(execute_file.find('clXYmodel') > -1):
          self.__log_write('[detect : {}]'.format(execute_file))
          files_list = os.listdir(os.getcwd())
          if(not execute_file in files_list):
            self.__log_write('[Error ! : can not find execute_file!]')
            info = False
          else:
            execute_file = './' + execute_file 
            operate_set.append(execute_file) 
            operate_set.append(result_dir)
            operate_set.append(str(int(param_dict['N_thermalize']))) 
            operate_set.append(str(int(param_dict['Ns']))) 
            operate_set.append(str(param_dict['T']))
            operate_set.append(str(int(param_dict['N_time']))) 
            operate_set.append(str(param_dict['t']))
            operate_set.append(str(int(param_dict['n_bin'])))
            operate_set.append(str(int(param_dict['N_loop']))) 
            operate_set.append(str(int(param_dict['N_parallel']))) 
            operate_set.append(str(int(param_dict['N_time_resolve']))) 
            operate_set.append(str(int(param_dict['Ns_observe']))) 
            log_file_name = self.__log_file_name
            log_open = open(log_file_name,'a')
            self.__log_write('[command line input]')
            self.__log_write('{}'.format(operate_set))
  
        elif(execute_file.find('MPO') > -1):
            self.__log_write('[detect : {}]'.format('MPO'))
            files_list = os.listdir(os.getcwd())
            if(not execute_file in files_list):
                self.__log_write('[Error ! : can not find execute_file!]')
                info = False
            else:
                operate_set.append('python') 
                operate_set.append(execute_file) 
                operate_set.append(result_dir)
                operate_set.append(str(int(param_dict['N']))) 
                operate_set.append(str(int(param_dict['D']))) 
                operate_set.append(str(param_dict['J']))
                operate_set.append(str(param_dict['h']))
                operate_set.append(str(param_dict['V']))
                operate_set.append(str(param_dict['coef']))
                operate_set.append(str(param_dict['t']))
                operate_set.append(str(int(param_dict['N_time'])))
                operate_set.append(str(param_dict['T']))
                operate_set.append(str(int(param_dict['tagged'])))
                operate_set.append(str(param_dict['test_mode']))
                log_file_name = self.__log_file_name
                log_open = open(log_file_name,'a')
                self.__log_write('[command line input]')
                self.__log_write('{}'.format(operate_set))
  
        else:
            self.__log_write('[can not find !]')
  
        param_dict['result_dir'] = result_dir
        param_dict['execute_file'] = execute_file
        param_dict['time_info'] = {}
        start_time =  datetime.datetime.now() 
        param_dict['time_info']['start_time'] = start_time.strftime('%Y/%m/%d %H:%M:%S')
        json_log_file_name = result_dir + 'parameter.json'
        self.__json_set(param_dict,json_log_file_name)
        if(info):
            self.__log_write('[execute : {}]'.format(start_time.strftime('%Y/%m/%d %H:%M:%S')))
  
        if(len(operate_set) > 0):
            if(info):
                p = subprocess.Popen(operate_set,stdout=log_open,stderr=log_open)
                p.wait()
                return_value = p.wait()
                if(return_value != 0):
                    self.__log_write('[Abnormal termination detected : return_value : {}]'.format(return_value))
                    self.__reset_indent()
                    self.__log_write('[Error End !]')
                    self.__end_log_copy()
                    sys.exit()
                log_open.close()
  
        elif(execute_file.find('MPO') > -1):
            filename = result_dir + "result.dat"
            MPO_experiment(param_dict,filename,self)
  
        end_time = datetime.datetime.now()
        self.__log_write('[finish  : {}]'.format(end_time.strftime('%Y/%m/%d %H:%M:%S')))
        param_dict['time_info']['end_time'] = end_time.strftime('%Y/%m/%d %H:%M:%S')
        self.__json_set(param_dict,json_log_file_name)


