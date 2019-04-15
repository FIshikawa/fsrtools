# todo : make more convenient and readable 
from fsrtools._util import LogManager

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


def set_simulate_params_iterate_dict(simulate_params,execute_file,indent=0,log_file=None):
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

    if('clXYmodel' in execute_file or 'clSpindemo' in execute_file or 'fpu_thermalization' in execute_file):
        if('N_thermalize' in simulate_params.keys()):
            if(simulate_params['N_thermalize'] == 'Auto'):
                logman.log_write('[detect : N_thermalize: Auto]')
                if(not isinstance(simulate_params['Ns'],str) and not isinstance(simulate_params['Ns'],list)): 
                    if(execute_file.find('Cube') > 0):
                        simulate_params['N_thermalize'] =  simulate_params['Ns'] * simulate_params['Ns'] * simulate_params['Ns'] 
                    elif(execute_file.find('Square') > 0):
                        simulate_params['N_thermalize'] =  simulate_params['Ns'] * simulate_params['Ns'] 
                    elif(execute_file.find('Tesseract') > 0):
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
                    if(execute_file.find('Cube') > 0):
                        simulate_params['Ns'] =  np.power(simulate_params['num_particles'],1/3)  
                    elif(execute_file.find('Square') > 0):
                        simulate_params['Ns'] =  np.power(simulate_params['num_particles'],0.5)  
                    elif(execute_file.find('Tesseract') > 0):
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


    elif(execute_file.find('MPO') > -1):
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


def set_simulate_params(simulate_params,iterate_key_list,iterate_pair,execute_file):
    for i in range(len(iterate_key_list)):
        simulate_params[iterate_key_list[i]] = iterate_pair[i]

        if('clXYmodel' in execute_file or 'clSpindemo' in execute_file or 'fpu_thermalization' in execute_file):
            if( iterate_key_list[i] in ['Ns']):
                if(execute_file.find('Cube') > -1):
                    simulate_params['N_thermalize'] =  simulate_params['Ns'] * simulate_params['Ns'] * simulate_params['Ns'] 
                elif(execute_file.find('Square') > 0):
                    simulate_params['N_thermalize'] =  simulate_params['Ns'] * simulate_params['Ns'] 
                elif(execute_file.find('Tesseract') > 0):
                    simulate_params['N_thermalize'] =  simulate_params['Ns'] * simulate_params['Ns'] * simulate_params['Ns'] * simulate_params['Ns']
                else:
                    simulate_params['N_thermalize'] =  simulate_params['Ns']
                simulate_params['N_thermalize'] = int(simulate_params['N_thermalize']) 
            if( iterate_key_list[i] in ['num_particles']):
                if(execute_file.find('Cube') > 0):
                    simulate_params['Ns'] =  np.power(simulate_params['num_particles'],1/3)  
                elif(execute_file.find('Square') > 0):
                    simulate_params['Ns'] =  np.power(simulate_params['num_particles'],0.5)  
                elif(execute_file.find('Tesseract') > 0):
                    simulate_params['Ns'] =  np.power(simulate_params['num_particles'],1/4)  
                else:
                    simulate_params['Ns'] =  simulate_params['num_particles']
                simulate_params['Ns'] =  int(simulate_params['Ns'])
            if( iterate_key_list[i] in ['t','dt']):
                simulate_params['N_time'] =  int(simulate_params['t'] / simulate_params['dt'])


        elif(execute_file.find('MPO') > -1):
            if(iterate_key_list[i] == 'N'):
                simulate_params[iterate_key_list[i]] = int(iterate_pair[i])
                simulate_params['tagged'] = int(iterate_pair[i]) // 2
                simulate_params['D'] = int(iterate_pair[i]) * 2
            if( iterate_key_list[i] in ['t','dt']):
                simulate_params['N_time'] =  int(simulate_params['t'] / simulate_params['dt'])

    return simulate_params


