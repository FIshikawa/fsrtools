import re
from fsrtools.simulation_tools._manager_utils import integer_filter

def product_combination_generator(iterate_dict):
    total_length = 1 
    length_dict = {}
    combination_list = []
    if len(iterate_dict.keys()):
        for key in iterate_dict.keys():
            length_dict[key] = len(iterate_dict[key])
            total_length = total_length * len(iterate_dict[key])
        combination_list = [{} for x in range(total_length)]
        repeat_length = total_length
        previous_length = total_length
        for key, length in sorted(length_dict.items(), key=lambda x: -x[1]):
            repeat_length //= length
            for i in range(total_length):
                combination_list[i][key] = \
                    iterate_dict[key][ (i % previous_length) // repeat_length ]
            previous_length = repeat_length

    return combination_list 


def set_total_combinations(simulate_params,logger):
    simulate_params_temp = simulate_params.copy()
    iterate_dict = {}
    for key in simulate_params.keys():
        if isinstance(simulate_params[key], list):
            iterate_dict[key] = simulate_params[key]
            logger('[list input : {0} : {1}]'
                    .format(key, simulate_params[key]))
        elif isinstance(simulate_params[key], str):
            counter = 0
            local_variables = {}
            for key_t in simulate_params.keys():
                if key_t != key and \
                    re.search( r'\b' + key_t+ r'\b',simulate_params[key]):
                    counter += 1

                    if not isinstance(simulate_params[key_t], list) and \
                                not isinstance(simulate_params[key_t],str):

                        local_variables[key_t] = simulate_params[key_t]
            if len(local_variables) == counter:
                try:
                    calculated_value = \
                           eval(simulate_params[key],globals(),local_variables)
                    simulate_params_temp[key] = \
                                        integer_filter(calculated_value)
                except (NameError, SyntaxError) as err:
                    logger('[cannot evaluate the formurala]')
                    logger('[the error is : {}]'.format(err))
                    logger('["{}" is input as "{}"]'
                            .format(key, simulate_params[key]))

                    simulate_params_temp[key] = simulate_params[key]
                logger('[{0} : {1}]'.format(key, simulate_params_temp[key]))
            else:
                for key_t in local_variables.keys():
                    logger('{0} is as command: depend on changing {1}'
                            .format(key,key_t))

    total_combinations = product_combination_generator(iterate_dict)
    return simulate_params_temp,  total_combinations


