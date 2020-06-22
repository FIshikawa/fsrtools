import os
import json
import shutil
import subprocess
from fsrtools.utils import StopWatch
from fsrtools.utils import SettingManager
from fsrtools.utils import LogManager
from fsrtools.utils import set_total_combinations
from fsrtools.simulation_tools._manager_utils import set_execute_command
from fsrtools.simulation_tools._manager_utils import set_simulate_params
from fsrtools.simulation_tools._manager_utils import integer_filter

class SimulationManager:
    """Simulation manager class. 
        It manage executing simulations with the parameter file formed jason.

    Args:
        parameter_file (string) : Path to the paramter file (json).
        log_file (string) : Path to log file. 
        cout_tag (bool) : Standard output option.  
        test_mode (bool) : Test mdoe option.
        command_data(dict) : List of commands saved in fsrtools directory.
        structured_output (bool) : Structred output option, defalut True.
        ignore_abnormal_termination(bool):
                                    Ignoring abnormal termination.
                                    default False.

    """

    def __init__(self,
                 parameter_file=None, 
                 log_file=None, 
                 cout_tag=False, 
                 test_mode=False,
                 command_data=None,
                 structured_output=True,
                 ignore_abnormal_termination=False):

        self.structured_output = structured_output
        self.ignore_abnormal_termination = ignore_abnormal_termination
        self.test_mode = test_mode
        self.command_data = command_data 
        self.parameter_file = parameter_file

        if self.test_mode:
            log_file = 'test/log_test.dat'
            cout_tag = True

        current_directory = os.getcwd()
        log_file = os.path.join(current_directory, log_file)

        self.logger = LogManager(log_file=log_file,cout_tag=cout_tag)

        self.setter = SettingManager(self.logger) 

    def __call__(self):
        timer = StopWatch()

        self.logger('[start time : {}]'.format(timer.start()))
        if self.test_mode :
            self.logger('[test mode]')
        self.logger('[server name : {}]'.format('%s' % os.uname()[1]))
        self.logger('[set log file at : {}]'.format(self.logger.log_file))

        if self.ignore_abnormal_termination :
            self.logger('[ignoreing abnormal termination mode]')

        if self.parameter_file is None :
            raise ValueError('parameter file must be set')
        self.logger('[parameter file : {}]'.format(self.parameter_file))  
        json_file = open(self.parameter_file,'r')
        json_data = json.load(json_file)

        if self.test_mode:
            if json_data['experiment_dir'] != 'test/': 
                self.logger('[experiment_dir is not "test/" : set]')
                json_data['experiment_dir'] = 'test/'

        # declare experimnets info
        self.logger('[experiments information]')
        self.logger('[result directory : {}]'
                .format(json_data['experiment_dir']))

        self.setter.set_directory(json_data['experiment_dir'])
        num_experiments = len(json_data['experiments'])
        self.logger('[number of experiment : {}]'.format(num_experiments))

        for key, params in json_data['experiments'].items():
            num_of_params = len(params['simulate_params'])
            self.logger(' [{0} : number of simulate params: {1}]'
                        .format(key,num_of_params)) 

        if self.test_mode:
            for key0, params_dict in json_data['experiments'].items():
                self.logger('[{0}]'.format(key0))
                for key1, params in params_dict.items():
                    self.logger(' [{0}]'.format(key1))
                    for key2, param in params.items():
                        self.logger('   {0} : {1}'.format(key2, param))

        # set result directories 
        if self.structured_output:
            unique_name = timer.start_time(format='%Y-%m-%d-%H-%M-%S')
            top_directory = json_data['experiment_dir']
            total_directory = os.path.join(top_directory, unique_name)

            self.logger('[set result output directory : {}]'
                    .format(total_directory))
            self.setter.set_directory(total_directory)

        else:
            total_directory = json_data['experiment_dir']
            self.logger(
                '[structured output mode off : all results in {} directly]'
                .format(total_directory)
                )

        self.operate_experiments(json_data, total_directory)

    def operate_experiments(self, json_data, total_directory):
        timer = StopWatch()

        json_data['time_info'] = {}
        json_data['time_info']['start_time'] = timer.start()
        self.logger('[start time : {}]'.format(timer.start()))

        parameter_file_for_record = os.path.join(total_directory,
                                                 'parameter.json')
        self.setter.json_set(json_data, parameter_file_for_record)

        for tag, params in json_data['experiments'].items():
            self.logger('[{0}][start experiment : {1}]'
                            .format(tag, timer.lap_start()))
            self.logger.add_indent()
            params['experiment_params']['experiment_dir'] = total_directory
            params['experiment_params']['experiment_tag'] = tag

            self.operate_simulations(params, tag)

            self.logger.decrease_indent()
            self.logger('[{0}][end experiment : {1} : lap time : {2}]'
                    .format(tag, timer.lap_end(), timer.lap_time()))

        self.logger('[finish time : {}]'.format(timer.end()))
        self.logger('[duration : {}]'.format(timer.duration()))
        json_data['time_info']['finish_time'] = timer.end_time()
        json_data['time_info']['duration'] = timer.duration()
        self.setter.json_set(json_data, parameter_file_for_record)
        shutil.copy(self.logger.log_file,
                        os.path.join(total_directory,'log.dat'))

    def operate_simulations(self,params_original,experiment_tag):
        timer = StopWatch()

        experiment_params = params_original['experiment_params'].copy()
        simulate_params_original = params_original['simulate_params'].copy()

        experiment_directory = experiment_params['experiment_dir']
        self.logger('[check experiment directory : {}]'
                        .format(experiment_directory))

        self.setter.set_directory(experiment_directory)

        if self.structured_output:
            simulate_directory = os.path.join(experiment_directory,
                                              experiment_tag) 
            self.setter.set_directory(simulate_directory)
        else:
            simulate_directory = experiment_directory 

        self.logger('[simulate directory : {}]'.format(simulate_directory))
        experiment_params['experiment_dir'] = simulate_directory
        
        params_original['time_info'] = {}
        params_original['time_info']['start_time'] = timer.start()
        parameter_file_simulation = \
                        os.path.join(simulate_directory,'parameter.json')
        self.setter.json_set(params_original, parameter_file_simulation)
    
        command_name = experiment_params['command_name']
    
        simulate_params_original, total_combinations = \
            set_total_combinations(simulate_params_original,self.logger)
    
        num_total_combinations = len(total_combinations)

        simulate_number = 1
        if num_total_combinations:
            num_simulations = num_total_combinations
            self.logger('[total number of simulations : {}]'
                         .format(num_simulations))
            self.logger('[check iterate lists]')
            self.logger('[iterate combination list] : {}'
                         .format(total_combinations))
        else:
            self.logger('[total number of simulations : 1]')
            total_combinations.append(['NO_ITERATION'])
    
        for i in range(max(num_total_combinations,1)):

            if num_total_combinations:
                simulate_params = \
                set_simulate_params(simulate_params_original, 
                                    total_combinations[i],
                                    self.logger)
            else:
                simulate_params = simulate_params_original 
            self.logger('[simulation : number-{}]'.format(simulate_number))
            self.logger.add_indent()

            if self.structured_output:
                result_directory = \
                    os.path.join(simulate_directory,
                                 'number-' + str(simulate_number) + '/')
                self.setter.set_directory(result_directory)
            else:
                result_directory = simulate_directory

            self.execute_simulation(command_name,
                                    simulate_params,
                                    result_directory)

            simulate_number += 1
            self.logger.decrease_indent()
    
        params_original['time_info']['end_time'] = timer.end()
        params_original['time_info']['duration'] = timer.duration()
        self.setter.json_set(params_original,parameter_file_simulation)
        self.logger('[all simulations complete]')

    def execute_simulation(self,
                           command_name,
                           simulate_params,
                           result_directory):
        timer = StopWatch()
    
        executed_params = simulate_params.copy()
        executed_params['result_directory'] = result_directory

        records = {}
        records['command_name'] = command_name
        records['simulate_params'] = executed_params.copy()
        records['time_info'] = {}
        records['time_info']['start_time'] = timer.start()

        parameter_file_each = \
                        os.path.join(result_directory, 'parameter.json')
        self.setter.json_set(records,parameter_file_each)
    
        execute_command = set_execute_command(command_name,
                                              executed_params,
                                              self.logger,
                                              self.command_data)

        self.logger('[execute : {}]'.format(timer.start_time()))
        log_open = open(self.logger.log_file,'a')
        if self.logger.cout_tag:
            p = subprocess.Popen(execute_command)
        else:
            p = subprocess.Popen(execute_command,
                                 stdout=log_open,
                                 stderr=log_open)
        p.wait()
        log_open.close()
        return_value = p.wait()
        self.logger('[finish  : {}]'.format(timer.end()))

        records['time_info']['end_time'] = timer.end_time()
        records['time_info']['duration'] = timer.duration()

        if return_value != 0:
            remark = \
                'Abnormal termination : return : {}'.format(return_value)
            records['time_info']['remark'] = remark
            self.logger(remark)
            self.logger.reset_indent()
            self.logger('[Error End !]')
            self.setter.json_set(records,parameter_file_each)
            if not self.ignore_abnormal_termination :
                raise ValueError(remark)

        self.setter.json_set(records,parameter_file_each)

