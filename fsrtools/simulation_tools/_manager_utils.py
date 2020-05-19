import re

def set_execute_command(command_name,simulate_params,logger,command_data):
    execute_command = []
    if command_name in command_data.keys():
        logger('[detect : {}]'.format(command_name))
        command_list = command_data[command_name]
    else:
        logger('[can not find !]')
        raise ValueError('{} is not defined as command'
                                                .format(command_name))

    for key in command_list:
        if key in simulate_params.keys():
            execute_command.append(str(simulate_params[key]))
        else:
            execute_command.append(key)
    logger('[command_name line input]')
    logger('{}'.format(execute_command))

    return execute_command


def set_simulate_params(simulate_params,combination,logger):
    for key in combination.keys():
        simulate_params[key] = combination[key]
    simulate_params_temp = simulate_params.copy()
    for key in simulate_params.keys():
        if isinstance(simulate_params[key], str):
            local_variable_dict = {}
            for key_t in simulate_params.keys():
                if key_t != key and \
                    re.search( r'\b' + key_t+ r'\b',simulate_params[key]):
                    local_variable_dict[key_t] = simulate_params[key_t]
            try:
                calculated_value  = \
                    eval(simulate_params[key],globals(),local_variable_dict)
                simulate_params_temp[key] = integer_filter(calculated_value)
            except (NameError, SyntaxError) as err:
                simulate_params_temp[key] = simulate_params[key]

    return simulate_params_temp


def integer_filter(n):
    if isinstance(n, int):
        return n
    elif isinstance(n, float):
        if n.is_integer():
            return int(n)
        else:
            return n
    else:
        return n
