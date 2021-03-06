import pytest
import json
import shutil
import os
from fsrtools.simulation_tools._manager_utils import *
from fsrtools.utils.set_total_combinations import *
from fsrtools.simulation_tools import SimulationManager
from test_command_manager import CommandManagerTest

def test_integer_filter():
    assert isinstance(integer_filter(10.0),int)
    assert isinstance(integer_filter(1),int)
    assert isinstance(integer_filter('hello'),str)


def test_product_combination_generator_case_1():
    iterate_dict = {'Na':[1,2,3,4],'Nb':[5,6,7],'Nc':[8,9]}
    combination_list = product_combination_generator(iterate_dict)
    assert len(combination_list) == 24
    for i in range(12):
        for j in range(12):
            if(i != j):
                counter = 0
                for key in iterate_dict.keys():
                    if(combination_list[i][key] == combination_list[j][key]):
                        counter += 1
                if(counter == 3):
                    print('{0} : {1} : {2}'.format(i,j,combination_list[i]))
                assert counter < 3


def test_product_combination_generator_case_2():
    iterate_dict = {'Na':[1,2,3],'Nb':[4,5,6],'Nc':[7,8]}
    combination_list = product_combination_generator(iterate_dict)
    assert len(combination_list) == 18
    for i in range(12):
        for j in range(12):
            if(i != j):
                counter = 0
                for key in iterate_dict.keys():
                    if(combination_list[i][key] == combination_list[j][key]):
                        counter += 1
                if(counter == 3):
                    print('{0} : {1} : {2}'.format(i,j,combination_list[i]))
                assert counter < 3


def test_set_simulate_params_iterate_dict_case_1():
    simulate_params = {'Ns':2,"N_time":'Ns*2'}
    print_temp = lambda sentence : print(sentence)
    simulate_params, total_combination = set_total_combinations(simulate_params,print_temp)
    assert simulate_params['N_time'] == 4
    assert len(total_combination) == 0


def test_set_simulate_params_iterate_dict_case_2():
    simulate_params = {'Nm':[1,2],'Ns':[2,3],'N_time':'Ns*Nm'}
    print_temp = lambda sentence : print(sentence)
    simulate_params, total_combination = set_total_combinations(simulate_params,print_temp)
    answer_dict = [{} for x in range(4)]
    counter = 0
    for value in simulate_params['Nm']:
        for value_t in simulate_params['Ns']:
            answer_dict[counter] = {'Nm':value,'Ns':value_t}
            counter += 1
    assert len(total_combination) == 4
    for i in range(len(total_combination)):
        assert total_combination[i] == answer_dict[i]


def test_set_simulate_params():
    simulate_params = {'Nm':[1,2],'Ns':2,'N_time':'Ns*Nm'}
    print_temp = lambda sentence : print(sentence)
    simulate_params_original, total_combination = set_total_combinations(simulate_params,print_temp)
    for i, pair in enumerate(total_combination):
        simulate_params_temp = set_simulate_params(simulate_params_original,pair)
        print(simulate_params_temp)
        assert simulate_params_temp['N_time'] == simulate_params['Nm'][i] * simulate_params['Ns']


@pytest.fixture(scope='module')
def set_data_for_test():
    files_list = os.listdir('./test/')
    command_manager = CommandManagerTest()
    if('hello_world' in command_manager.command_name_list):
        command_manager.remove_command('hello_world')
    command_manager.add_command({'hello_world' : ['python','./test/hello_world.py','N_loop']})
    command_manager.save()
    pytest.log_file = 'test/log.dat'
    pytest.parameter_json = 'test/parameter_test.json'
    pytest.command_data = command_manager.command_data
    yield set_data_for_test
    command_manager.save()
    files_list_created = os.listdir('./test/')
    for key in list(set(files_list_created) - set(files_list)):
        try:
            os.remove(os.path.join('./test',key))
        except OSError as now_error:
            shutil.rmtree(os.path.join('./test',key))


def test_operate_experiments(set_data_for_test):
    log_file = pytest.log_file
    parameter_json = pytest.parameter_json
    command_data = pytest.command_data
    simulate_manager = SimulationManager(
                                         parameter_file=parameter_json,
                                         log_file=log_file,
                                         test_mode=True,
                                         command_data=command_data
                                         )
    simulate_manager()

