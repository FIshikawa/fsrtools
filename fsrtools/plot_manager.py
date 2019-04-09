import sys
import os
import json
import copy
from matplotlib import cm
import matplotlib.pyplot as plt 
import matplotlib.ticker as ptick
from scipy.stats import norm
from scipy.stats import cauchy
from mpl_toolkits.mplot3d import axes3d
from scipy import stats
import math
import numpy as np

class PlotManager:
    def __init__(self,top_directory=None,file_name=None):
        self.__plot_kind = ['hist','correlation', 'normal','totally']
        self.ax = {}
        self.fig = {}
        self.__plot_type = {}
        for key in self.__plot_kind:
            self.ax[key] = {}
            self.__plot_type[key] = []
        self.basic_size = {'window_large':20,'window_small':8,'font':20}
        self.__result_whole_info = ''
        self.__result_info = ''
        self.__data_dir_list = []
        self.__variable_params = []
        self.__num_patterns_with_variable_params = []
        self.__common_params = []
        self.__indent = 0
        self.__label = ''
        self.__buffer_data = {}
        self.__top_directory = top_directory

        if(top_directory != None):
            self.__set_result_info(top_directory)
        if(file_name != None):
            file_in_dir_name = os.path.dirname(file_name)
            self.__set_result_info(file_in_dir_name)


    def __set_result_info(self,top_directory):
        sentence = '  [results whole info] \n' 
        result_list = []
        experiment_date= []
        previous_dir = ''
        indent = 0
        previous_length = 0

        if(len(top_directory) < 1):
            sentence += '    [not find particular structure : instant plot mode]\n'
            self.__result_whole_info = sentence
            sentence = '  [results with params] '
            self.__result_info = sentence

        else:
            top_len = len([x for x in top_directory.split('/') if(len(x) > 0)])
            counter = 0
            variable_params = []
            common_params = []
            current_dir_list = []

            for current_dir, included_dir, files in os.walk(top_directory):
                current_dir_list = current_dir.split('/') 
                indent = len(current_dir_list)

                if(len(included_dir) < 1 and len([x for x in files if 'result' in x]) > 0):
                    counter += 1
                    sentence += '[{}]'.format(counter) 
                    if(counter > 0): 
                        for i in range(indent-top_len - int(math.log10(counter)) - 1): # log10 is for length of output
                            sentence += '  '
                    self.__data_dir_list.append('{}'.format(current_dir))
                else:
                    for i in range(indent-top_len ):
                        sentence += '  '
                sentence = sentence + '[{}]'.format(current_dir) + '\n'

                if('experiment_' in current_dir_list[-1]):
                    indent_t = ''
                    for i in range(indent-top_len + 1):
                        indent_t += '  '
                    json_file = open(os.path.join(current_dir,'parameter.json'),'r')
                    json_data = json.load(json_file)
                    experiment_date.append(current_dir_list[-2])
                    self.__num_patterns_with_variable_params.append(0)
                    self.__variable_params.append({})
                    self.__common_params.append({})
                    self.__common_params[-1]['execute_file'] = json_data['experiment_params']['execute_file']
                    for key in json_data['simulate_params'].keys():
                        if(not 'dir' in key and not 'time_info' in key):
                            if(isinstance(json_data['simulate_params'][key], list)):
                                self.__variable_params[-1][key] = []
                            else:
                                self.__common_params[-1][key] = json_data['simulate_params'][key]
                    sentence += indent_t + '[common parameter]'
                    sentence += '\n' + indent_t + '  execute_file : {}'.format(self.__common_params[-1]['execute_file']) 
                    for key in self.__common_params[-1]:
                        sentence = sentence + '\n' + indent_t + '  {0} : {1}'.format(key,self.__common_params[-1][key])
                    sentence += '\n' + indent_t + '[varibale parameter]'
                    for key in self.__variable_params[-1].keys():
                        sentence += '\n' + indent_t + '  ' +  key  
                    sentence += '\n'

                if(len(included_dir) < 1):
                    garbage = []
                    json_file_name = ''
                    for key in files:
                        if('parameter.json' in key):
                            json_file_name = key
                        if('results' in key):
                            garbage.append(key)
                    for key in garbage:
                        files.remove(key)
                    for i in range(indent-top_len):
                        sentence += '  '

                    if(len(files) < 1):
                        sentence = sentence + '  No Result Files \n'
                    elif(len(json_file_name) < 1):
                        sentence = sentence + '  No parameter file \n'
                    else:
                        json_file = open(os.path.join(current_dir,json_file_name),'r')
                        json_data = json.load(json_file)
                        result_list.append(files)
                        sentence = sentence + '  {}'.format(files) + '\n'
                        indent_t = ''
                        for i in range(indent-top_len+1):
                            indent_t += '  '
                        if(len(self.__variable_params) > 0):
                            sentence += indent_t + '  [variable parameters]'
                            for key in self.__variable_params[-1].keys():
                                sentence = sentence +  '  {0} : {1}  '.format(key,json_data[key]) 
                                self.__variable_params[-1][key].append(json_data[key])
                            self.__num_patterns_with_variable_params[-1] += 1
                        else:
                            sentence += indent_t + '  [parameters]'
                            for key in json_data.keys():
                                sentence = sentence +  '  {0} : {1}  '.format(key,json_data[key]) 
                        sentence += '\n'
            self.__result_whole_info = sentence

            sentence = '  [results with params] '
            if(len(self.__common_params[:]) > 0):
                counter = 1
                for i in range(len(self.__common_params[:])):
                    sentence += '\n    [experiment_{0}] [date : {1}] \n      [common params]  '.format(i+1,experiment_date[i])
                    for key in self.__common_params[i].keys():
                        sentence += key + ' : {}, '.format(self.__common_params[i][key])
                    for j in range(self.__num_patterns_with_variable_params[i]):
                        sentence += '\n        [{}] '.format(counter)
                        for key in self.__variable_params[i].keys():
                            sentence += key + ' : {}, '.format(self.__variable_params[i][key][j]) 
                        sentence += ' {}'.format(result_list[counter-1])
                        counter += 1
            elif(len(json_file_name) < 1):
                sentence += '\n    [parameters] [no data : cannot find parameter file]' 
                sentence += '\n    [result files] : {}'.format(files)
            else:
                sentence += '\n    [parameters] [date : {}]'.format(current_dir_list[-3])
                for key in json_data.keys():
                    sentence = sentence +  '\n      {0} : {1}  '.format(key,json_data[key]) 
                sentence += '\n    [result files] : {}'.format(files)
            self.__result_info = sentence


    def __directory_name_set(self,file,directory):
        directory_name = ''
        if(isinstance(file, str)):
            if('/' in file):
                directory_name = os.path.dirname(file)
        if(directory != None):
            if(isinstance(directory, int)): 
                directory_name = self.__data_dir_list[directory-1]
            elif(isinstance(directory, basestring)): 
                directory_name = directory
        else:
            if(len(self.__data_dir_list) != 1):
                self.__myprint('[No directory name : instant plot]')
            else:
                directory_name = self.__data_dir_list[0]
                self.__myprint('[Automatically set directory : {}]'.format(directory_name))
        return directory_name


    def __file_name_set(self,file,directory):
        file_name = ''
        if('/' in file):
            directory_name = os.path.dirname(file)
        else:
            directory_name = self.__directory_name_set(file,directory)
            file_name = os.path.join(directory_name, file)
            self.__myprint('[directory set : {}]'.format(directory_name))
            file_in_dir_name = directory_name
        self.__myprint('[full path of target : {}]'.format(file_name))
        return file_name 


    def __check_json_file(self,directory_name):
        json_file_name = ''
        files_in_dir = os.listdir(directory_name)
        for key in files_in_dir:
            if('.json' in key):
                json_file_name = key 
                break
        if(len(json_file_name) < 1):
            self.__myprint('[cannot find parameter file : unset parameter file mode]')
        else:
            json_file_name =  os.path.join(directory_name,json_file_name)
            self.__myprint('[read parameter : {}]'.format(json_file_name))
            json_file = open(json_file_name,'r')
            json_data = json.load(json_file)
            self.__myprint('[parameters in this simulation]')
            for key in json_data.keys():
                self.__myprint('  [{0} : {1} ]'.format(key,json_data[key]))
            return json_data


    def __data_load(self,file_name,plot_kind):
        type_dict = {}
        if(not file_name in self.__buffer_data.keys()):
            data = {}
            if(plot_kind == None):
                self.__myprint('[plot_kind is not input : automatically set]')
                for key in self.__plot_kind:
                    if(key in file_name):
                        plot_kind = key
                        self.__myprint('[set plot_kind {} : {} in the result file name]'.format(plot_kind,plot_kind))
                if(plot_kind == None):
                    if('_' in file_name.split('/')[-1]):
                        self.__myprint('[detect "_" but cannot find particular case.]')
                    self.__myprint('[normal plot data]')
                    plot_kind = 'normal'
            else:
                if(not plot_kind in self.__plot_kind):
                    self.__myprint('[Error! : input plot_kind is not in our set]')
                    sys.exit()
                else:
                    self.__myprint('[input plot_kind : {}]'.format(plot_kind))

            if(plot_kind == 'normal'):
                type_dict = {'ACF_list' : [],
                             'With_error_list' : [],
                             'Energy_list' : [],
                             'Rest_list' : [],
                             'Exact_list' : [],
                             'x_axis' : ''}
                data_t = np.loadtxt(file_name, dtype = np.float64,skiprows=1)
                f = open(file_name,'r')
                value_keys = f.readline()
                value_keys = value_keys.strip()
                value_keys = value_keys.split(' ')
                value_keys.pop(0)
                data[value_keys[0]] = data_t[:,0]
                type_dict['x_axis'] = value_keys[0]
                for key in value_keys[1:]:
                    data[key] = data_t[:,value_keys.index(key)]
                    if('exact' in key):
                        type_dict['Exact_list'].append(key)
                    elif('ACF' in key):
                        if(not 'fourier' in key and not 'error' in key):
                            type_dict['ACF_list'].append(key)
                    elif(not 'error' in key):
                        if('Energy' in key):
                            if('error_' + key in value_keys):
                                type_dict['Energy_list'].append(key)
                                type_dict['With_error_list'].append(key)
                            else:
                                type_dict['Rest_list'].append(key)
                        elif('error_' + key in value_keys):
                            type_dict['With_error_list'].append(key)
                        else:
                            type_dict['Rest_list'].append(key)

            elif(plot_kind in ['hist','correlation']):
                data_t = np.loadtxt(file_name, dtype = np.float64,skiprows=2)
                f = open(file_name,'r')
                x_data = f.readline()
                x_data = x_data.strip()
                x_data = x_data.split(' ')
                x_data.pop(0)
                data[x_data[0]] = np.zeros(len(x_data[1:]))
                for i in range(len(x_data[1:])):
                    data[x_data[0]][i] = x_data[1+i]
                value_keys = f.readline()
                value_keys = value_keys.strip()
                value_keys = value_keys.split(' ')
                value_keys.pop(0)

                if(plot_kind == 'hist'):
                    type_dict = { 'y_axis' : '',
                                  'values' : [],
                                  '3d_plot':[],
                                  '2d_plot':[]
                                }
                    type_dict['y_axis'] = x_data[0]
                    type_dict['values'].append(value_keys[0].split('_')[-1])
                    for key in value_keys:
                        key_t = key.split('_')[-1]
                        if(not key_t in type_dict['values']):
                            type_dict['values'].append(key_t)

                    for key in type_dict['values']:
                        type_dict['3d_plot'].append(key + '_3d_plot')
                        type_dict['2d_plot'].append(key + '_2d_plot_head')
                        type_dict['2d_plot'].append(key + '_2d_plot_tail')
                        type_dict['2d_plot'].append(key + '_2d_plot')
                        data[key] = {}
                        data[key]['range'] = data_t[:,[x for x in range(len(value_keys)) if 'range' in value_keys[x] and key in value_keys[x]]]
                        data[key]['hist'] = data_t[:,[x for x in range(len(value_keys)) if 'hist' in value_keys[x] and key in value_keys[x]]]

                elif(plot_kind == 'correlation'):
                    data_t = np.loadtxt(file_name, dtype = np.float64,skiprows=2)
                    type_dict = { 'y_axis' : '',
                                  'x_axis' : '',
                                  'values' : [],
                                  '3d_plot':[],
                                  '2d_plot':[]
                                }
                    type_dict['y_axis'] = x_data[0]
                    type_dict['x_axis'] = value_keys[0]
                    data[value_keys[0]] = data_t[:,0]
                    type_dict['values'].append(value_keys[1])
                    for key_t in value_keys[1:]:
                        if(not key_t in type_dict['values']):
                            type_dict['values'].append(key_t)
                    for key in type_dict['values']:
                        type_dict['3d_plot'].append(key + '_3d_plot')
                        type_dict['2d_plot'].append(key + '_2d_plot')
                        data[key] = data_t[:,[x for x in range(len(value_keys)) if key in value_keys[x]]]

            elif(plot_kind == 'totally'):
                type_dict = {'y_list' : [],
                             'x_axis' : ''}
                data_t = np.loadtxt(file_name, dtype = np.float64,skiprows=1)
                f = open(file_name,'r')
                value_keys = f.readline()
                value_keys = value_keys.strip()
                value_keys = value_keys.split(' ')
                value_keys.pop(0)
                data[value_keys[0]] = data_t[:,0]
                type_dict['x_axis'] = value_keys[0]
                for key in value_keys[1:]:
                    data[key] = data_t[:,value_keys.index(key)]
                    type_dict['y_list'].append(key)

            self.__buffer_data[file_name] = {}
            self.__buffer_data[file_name]['data']      = copy.deepcopy(data)
            self.__buffer_data[file_name]['type_dict'] = copy.deepcopy(type_dict)
            self.__buffer_data[file_name]['plot_kind'] = copy.deepcopy(plot_kind)

        else:
            self.__myprint('[data is already bufferd]')
            data      = copy.deepcopy(self.__buffer_data[file_name]['data'])
            type_dict = copy.deepcopy(self.__buffer_data[file_name]['type_dict'])
            plot_kind = copy.deepcopy(self.__buffer_data[file_name]['plot_kind'])

        return data, type_dict, plot_kind


    def __set_fig_ax(self,type_dict,plot_kind,plot_value,directory):
        self.__myprint('[set fig and ax]')
        self.__add_indent()
        total_number_of_plot = 0
        if(plot_value == None and plot_kind != 'totally'):
            self.fig[plot_kind] = plt.figure(figsize=(self.basic_size['window_large']*1.618,self.basic_size['window_large']))
            self.fig[plot_kind].subplots_adjust(left=0.075, bottom=0.05, right=0.95, top=0.95, wspace=0.15, hspace=0.15)

            if(plot_kind == 'normal'):
                total_number_of_plot = len(type_dict['ACF_list']) + len(type_dict['With_error_list']) +  len(type_dict['Rest_list']) + (1 if len(type_dict['Energy_list']) > 0 else 0) 
            
            elif(plot_kind in ['hist','correlation']):
                total_number_of_plot = len(type_dict['3d_plot']) + len(type_dict['2d_plot']) 

            elif(plot_kind == 'totally'):
                total_number_of_plot = 1

            self.__myprint('[total number of plot : {}]'.format(total_number_of_plot))
            if(total_number_of_plot != 1):
                if((total_number_of_plot % 3) == 0):
                    vertical_length = 3
                    horizontal_length = int(total_number_of_plot / vertical_length) 
                elif((total_number_of_plot % 2) == 0):
                    vertical_length = 2
                    horizontal_length = int(total_number_of_plot / vertical_length) 
                else:
                    vertical_length = 3
                    horizontal_length = int(total_number_of_plot / vertical_length) + 1

            if(plot_kind == 'normal'):
                counter = 1
                for key_t in ['ACF_list','With_error_list','Rest_list']:
                    for key in type_dict[key_t]:
                        self.ax[plot_kind][key] = self.fig[plot_kind].add_subplot(vertical_length, horizontal_length,counter)
                        counter += 1
                if(len(type_dict['Energy_list']) > 0):
                    value_name = 'Energy_totaly_plot'
                    self.ax[plot_kind][value_name] = self.fig[plot_kind].add_subplot(vertical_length, horizontal_length,counter)

            elif(plot_kind in ['hist','correlation']):
                counter = 1
                for key in type_dict['2d_plot']:
                    self.ax[plot_kind][key] = self.fig[plot_kind].add_subplot(vertical_length, horizontal_length,counter)
                    counter += 1
                for key in type_dict['3d_plot']:
                    self.ax[plot_kind][key] = self.fig[plot_kind].add_subplot(vertical_length, horizontal_length,counter,projection='3d')
                    counter += 1

        elif(plot_kind == 'totally'):
            plot_value = 'Totally_plot'
            self.fig[plot_kind], self.ax[plot_kind][plot_value] = plt.subplots(figsize=(self.basic_size['window_small']*1.618*1.5,self.basic_size['window_small']*1.5))

        else:
            self.__myprint('[plot_value is input : {}]'.format(plot_value))
            self.__myprint('[plot_kind  is input : {}]'.format(plot_kind))
            check_list = []
            if(plot_kind == 'normal'):
                check_list.extend([x for x in type_dict.keys() if x != 'Energy_list' and x != 'x_axis']) 
            elif(plot_kind in ['correlation','hist']):
                check_list.extend([x for x in type_dict.keys() if x != 'y_axis' and x != 'x_axis' and x != 'values']) 

            for key in check_list:
                if(plot_value in type_dict[key]): 
                    self.__myprint('[detect : plot_value in : {}]'.format(key))
                    key_t = key
                    del type_dict[key][:]
                    type_dict[key].append(plot_value)
                    if(plot_value in self.ax[plot_kind].keys()):
                      self.__myprint('[{} is already set in {} plots : added into target plot]'.format(plot_value,plot_kind))
                    else:
                      self.__myprint('[plot_value is not in axes keys : create]')
                      self.fig[plot_kind], self.ax[plot_kind][plot_value] = plt.subplots(figsize=(self.basic_size['window_small']*1.618,self.basic_size['window_small']))
                else:
                    del type_dict[key][:]

            if(plot_kind == 'normal'):
                if(plot_value == 'Energy_totally_plot'):
                    if(plot_value in self.ax[plot_kind].keys()):
                        self.__myprint('[{} is already set in {} plots : added into target plot]'.format(plot_value,plot_kind))
                    else:
                        self.__myprint('[plot_value is not in axes keys : create]')
                        self.fig[plot_kind], self.ax[plot_kind][plot_value] = plt.subplots(figsize=(self.basic_size['window_small']*1.618,self.basic_size['window_small']))
                else:
                    del type_dict['Energy_list'][:]


            if(len([x for x in check_list if len(type_dict[x]) > 0]) < 1):
                self.__myprint('[Error! plot_value is not in {} plots]'.format(plot_kind))
                sys.exit()
            else:
                if(isinstance(directory, int)): 
                    directory_t = 0
                    for i in range(len(self.__common_params)):
                        for j in range(self.__num_patterns_with_variable_params[i]):
                            directory_t += 1
                            if(directory == directory_t):
                                for key in self.__variable_params[i].keys():
                                    self.__label = '{0} : {1}, '.format(key, self.__variable_params[i][key][j])
                                break
                        else:
                            continue
                        break

        self.__decrease_indent()


    def plot_data(self,data=None,data_x=None,data_y=None,data_z=None,y_error=None,ptype=None,x_axis=None,y_axis=None,z_axis=None,label=None,title=None,addplot=None,x_lim=None,y_lim=None,marker=None):
        if(addplot != None and isinstance(addplot,list)):
            plot_kind = addplot[0]
            value_name = addplot[1]
            if(not plot_kind in self.fig.keys() or not value_name in self.ax[plot_kind].keys()):
                self.__myprint('[Error!! : add target does not exist!!]')
        else:
            plot_kind= 'temporary'
            value_name = 'temporary'
        data_list = []
        data_dict = {}
        axis_list = []
        data_list.extend([data_x,data_y,data_z,y_error])
        axis_list.extend([x_axis,y_axis,z_axis])

        if(ptype == '2d'):
            if(not plot_kind in self.fig.keys() or not value_name in self.ax[plot_kind].keys()):
                self.ax[plot_kind] = {}
                self.fig[plot_kind], self.ax[plot_kind][value_name] = plt.subplots(figsize=(self.basic_size['window_small']*1.618,self.basic_size['window_small']))
                self.__myprint('[Remark : fig and ax key of plot_data is "temporary", You can overlay some graph on same window which is identified by the key "temporary"]')
        else:
            if((len([x for x in axis_list if x != None]) + (1 if title != None else 0)) < 1 and len([x for x in data_list if x != None]) > 0): 
                self.__myprint('[Error!! : ptype must be chosen from "2d" or "3d"]')
                sys.exit()

        if(data == None and ptype != None):
            self.__plot_2d(self.ax[plot_kind][value_name],data_x,data_y,y_error=y_error,label=label,marker=marker)

        elif(isinstance(data,dict) and ptype != None):
            for i in range(4):
                if(data_list[i] != None):
                    if(not isinstance(data_list[i],str)):
                        self.__myprint('[Error! : data_xyz, y_error shold be str]') 
                        sys.exit()
                    else:
                        if(data_list[i] in data.keys()):
                            data_dict[i] = data[data_list[i]]
                        else:
                            self.__myprint('[Error! : {} is not in data]'.format(data_list[i])) 
                            sys.exit()
                else:
                    data_dict[i] = None

            if(axis_list[0] == None):
                self.ax[plot_kind][value_name].set_xlabel(data_list[0])
            if(axis_list[1] == None):
                self.ax[plot_kind][value_name].set_ylabel(data_list[1])

            self.__plot_2d(self.ax[plot_kind][value_name],data_dict[0],data_dict[1],y_error=data_dict[3],label=label,marker=marker)

        if(x_lim != None):
            if(isinstance(x_lim,dict)):
                self.ax[plot_kind][value_name].set_xlim(left=x_lim[0],right=x_lim[1])

        if(y_lim != None):
            if(isinstance(y_lim,dict)):
                self.ax[plot_kind][value_name].set_ylim(bottom=y_lim[0],top=y_lim[1])

        if(label != None):
            self.ax[plot_kind][value_name].legend(loc="upper right",fontsize=self.basic_size['font'])

        if(title != None):
            self.ax[plot_kind][value_name].set_title(title)

        for key in [x for x in axis_list if x != None]:
            if(not isinstance(key,str)):
                self.__myprint('[Error! : xyz_axis shold be str]') 
            else:
                if(axis_list.index(key) == 0):
                    self.ax[plot_kind][value_name].set_xlabel(key)
                elif(axis_list.index(key) == 1):
                    self.ax[plot_kind][value_name].set_ylabel(key)
                elif(axis_list.index(key) == 2):
                    self.ax[plot_kind][value_name].set_zlabel(key)


    def plot_result(self,file=None,directory=None,plot_kind=None,plot_value=None,save_fig=False,log_scale=False):
        self.__init_indent()
        directory_name = ''
        directory_name = self.__directory_name_set(file,directory)
        if(len(directory_name) < 1):
            self.__myprint('[instant plot mode]')
        elif('experience' in directory_name.split('/')[-2]):
            self.__myprint('[detect phrase "experience" : result files not in ]')
            sys.exit()
        elif('number' in directory_name.split('/')[-2] and file == None):
            self.__myprint('[detect phrase "number" : plot all results here]')

        if(file != None):
            self.__myprint('[file plot mode]')
            self.__myprint('[file name : {}]'.format(file))
            file_name = ''
            file_name = self.__file_name_set(file,directory)
            if(not os.path.exists(file_name)):
                self.__myprint('[Error! : {} does not exist]'.format(file)) 
                sys.exit()

        else:
            self.__myprint('[error!! cannot decide plot files : select number dir or result file]')

        if(len(directory_name) < 1):
            self.__myprint('[instant plot mode : no parameter.json]')
            json_data = None
        else:
            files_in_dir = os.listdir(directory_name)
            self.__myprint('[check files in the directory]')
            self.__myprint(files_in_dir)
            json_data = self.__check_json_file(directory_name)
            waste_files = []
            for key in files_in_dir:
                if('result' in key):
                    waste_files.append(key)
            for key in waste_files:
                files_in_dir.remove(key)
            self.__myprint('[start ploting]')

        if(directory != None and file == None):
            self.__myprint('[plot only "result" files such as]')
            self.__add_indent()
            self.__myprint('  {}'.format(files_in_dir))
            self.__decrease_indent()
            self.__add_indent()
            for key in files_in_dir:
                self.__plot_file(directory_name + key,directory,json_data,plot_kind=plot_kind,plot_value=plot_value,log_scale=log_scale)
                if(save_fig):
                    fig_name = directory_name + key.split('.')[0] + '.pdf'
                    self.__myprint('[save figure : {}]'.format(fig_name))
                    plt.savefig(fig_name,format='pdf')

        else:
            self.__add_indent()
            if(json_data is None and plot_kind is None):
                plot_kind = 'totally' 
                self.__myprint('[no input plot_kind : plot_kind set as "totally" automatically]')
            self.__plot_file(file_name,directory,json_data,plot_kind=plot_kind,plot_value=plot_value,log_scale=log_scale)  
            if(save_fig):
                fig_name = file_name.split('/')[-1]
                fig_name = directory_name + fig_name.split('.')[0] + '.pdf'
                self.__myprint('[save figure : {}]'.format(fig_name))
                plt.savefig(fig_name,format='pdf')


        self.__decrease_indent()
        self.__myprint('[plot completed]')

    def __plot_file(self,file_name,directory,params_dict=None,legend_str=None,plot_kind=None,plot_value=None,log_scale=False):
        plt.rcParams["font.size"] = self.basic_size['font']
        if(params_dict != None):
            if('T' in params_dict.keys()):
                T = params_dict['T']
            if('t' in params_dict.keys() and 'N_time' in params_dict.keys()):
                dt = params_dict['t'] / float(params_dict['N_time'])
            if('t' in params_dict.keys()):
                t = params_dict['t']
            if('N_time_resolve' in params_dict.keys()):
                N_time_resolve = params_dict['N_time_resolve']

        data, type_dict, plot_kind = self.__data_load(file_name,plot_kind)

        self.__add_indent()
        for key in type_dict.keys():
            self.__myprint('[{0}] : {1}'.format(key,type_dict[key]))
        self.__decrease_indent()

        if(plot_kind == 'hist'):
            self.__myprint('[hist plot]')
            del self.__plot_type[plot_kind][:]
            self.__add_indent()
            self.__set_fig_ax(type_dict,plot_kind,plot_value,directory)

            for key in type_dict['2d_plot']:
                for value_name in type_dict['values']:
                    if(value_name in key):
                        self.__myprint('[plot : {}]'.format(key))
                        self.__add_indent()
                        self.__plot_type[plot_kind].append(key)
                        if('head' in key or 'tail' in key):
                            axis_num = (0 if 'head' in key else -1)
                            self.__genuine_hist_plot(data[value_name]['range'][:,axis_num],data[value_name]['hist'][:,axis_num],self.ax[plot_kind][key])
                            self.__process_hist_plot(data[value_name]['range'][:,axis_num],data[value_name]['hist'][:,axis_num],self.ax[plot_kind][key])
                            if('Velocity' in key):
                                if(type_dict['y_axis'] in ['T','Temperture','temperture']):
                                    if('head' in key):
                                        self.__exact_gaussian_plot(data[value_name]['range'][:,axis_num],data[value_name]['hist'][:,axis_num],self.ax[plot_kind][key],data[type_dict['y_axis']][0])
                                    else:
                                        self.__exact_gaussian_plot(data[value_name]['range'][:,axis_num],data[value_name]['hist'][:,axis_num],self.ax[plot_kind][key],data[type_dict['y_axis']][-1])
                            self.ax[plot_kind][key].legend(loc="upper right",prop = {'size':self.basic_size['font']})
                        else:
                            self.__hist_plot_overlaid(data[value_name]['range'],data[value_name]['hist'],data[type_dict['y_axis']],self.ax[plot_kind][key],n_bin=100,N_plot=10,label=type_dict['y_axis'])
                        self.ax[plot_kind][key].set_title(key)
                        self.ax[plot_kind][key].set_xlabel(value_name)
                        self.ax[plot_kind][key].set_ylabel('{} Distribution'.format(value_name))
                        self.__decrease_indent()

            for key in type_dict['3d_plot']:
                for value_name in type_dict['values']:
                    if(value_name in key):
                        self.__myprint('[plot : {}]'.format(key))
                        self.__add_indent()
                        self.__plot_type[plot_kind].append(key)
                        self.__hist_plot_3d(data[value_name]['range'],data[value_name]['hist'],data[type_dict['y_axis']],self.ax[plot_kind][key],n_bin=100,N_plot=10)
                        self.ax[plot_kind][key].set_xlabel(value_name)
                        self.ax[plot_kind][key].set_ylabel(type_dict['y_axis'])
                        self.ax[plot_kind][key].set_zlabel('{} Distribution'.format(value_name))
                        self.ax[plot_kind][key].set_title(key)
                        self.__decrease_indent()
            self.__decrease_indent()

        elif(plot_kind == 'correlation'):
            self.__myprint('[correlation plot]')
            del self.__plot_type[plot_kind][:]
            self.__add_indent()
            self.__set_fig_ax(type_dict,plot_kind,plot_value,directory)

            for key in type_dict['2d_plot']:
                for value_name in type_dict['values']:
                    if(value_name in key):
                        self.__myprint('[plot : {}]'.format(key))
                        self.__plot_type[plot_kind].append(key)
                        self.__plot_2d_overlaid(data[type_dict['x_axis']],data[value_name],data[type_dict['y_axis']],self.ax[plot_kind][key],label=type_dict['y_axis'],N_plot=10)
                        self.ax[plot_kind][key].set_xlabel(type_dict['x_axis'])
                        self.ax[plot_kind][key].set_title(key)
                        self.ax[plot_kind][key].set_ylabel('{}'.format(value_name))

            for key in type_dict['3d_plot']:
                for value_name in type_dict['values']:
                    if(value_name in key):
                        self.__myprint('[plot : {}]'.format(key))
                        self.__plot_type[plot_kind].append(key)
                        self.__plot_3d(self.ax[plot_kind][key],data[type_dict['x_axis']],data[value_name],data[type_dict['y_axis']],N_plot=10)
                        self.ax[plot_kind][key].set_xlabel(type_dict['x_axis'])
                        self.ax[plot_kind][key].set_ylabel(type_dict['y_axis'])
                        self.ax[plot_kind][key].set_title(key)
                        self.ax[plot_kind][key].set_zlabel('{}'.format(value_name))
            self.__decrease_indent()

        elif(plot_kind == 'totally'):
            self.__myprint('[plot_kind detect : totally]')
            del self.__plot_type['totally'][:]
            self.__set_fig_ax(type_dict,plot_kind,plot_value,directory)
            value_name = 'Totally_plot'
            self.__plot_type[plot_kind].append(value_name)
            for counter, key in enumerate(type_dict['y_list']):
                self.ax[plot_kind][value_name].xaxis.set_tick_params(labelsize=self.basic_size['font']*1.5)
                self.ax[plot_kind][value_name].yaxis.set_tick_params(labelsize=self.basic_size['font']*1.5)
                value_axis = key
                label_t = key
                self.__myprint('[plot : {}]'.format(key))
                self.__add_indent()
                if(len(type_dict['y_list']) < 2):
                    self.__plot_2d(self.ax[plot_kind][value_name],data[type_dict['x_axis']],data[value_axis],label=label_t,log_scale=log_scale)
                else:
                    self.__plot_2d(self.ax[plot_kind][value_name],data[type_dict['x_axis']],data[value_axis],label=label_t,color=cm.rainbow(float(counter)/len(type_dict['y_list'])),log_scale=log_scale)
                self.ax[plot_kind][value_name].set_xlabel(type_dict['x_axis'],fontsize=self.basic_size['font']*1.5)
                self.ax[plot_kind][value_name].grid(which='both',color='black',linestyle='--')
                if('_' in file_name.split('/')[-1]):
                    self.__myprint('[file name has "_" : y-axis named by it]') 
                    self.ax[plot_kind][value_name].set_ylabel(file_name.split('/')[-1].split('_')[-1].split('.')[0],fontsize=self.basic_size['font']*1.5)
                else:
                    self.ax[plot_kind][value_name].set_ylabel(value_name,fontsize=self.basic_size['font']*1.5)
                self.ax[plot_kind][value_name].legend(bbox_to_anchor=(1.1, 1),loc="upper right",fontsize=self.basic_size['font'])
                self.__decrease_indent()

        elif(plot_kind == 'normal'):
            self.__myprint('[normal plot]')
            del self.__plot_type[plot_kind][:]
            self.__add_indent()
            self.__set_fig_ax(type_dict,plot_kind,plot_value,directory)

            for key in type_dict['ACF_list']:
                value_axis = key
                value_axis_error = 'error_' + key
                value_name = key
                self.__myprint('[plot : {}]'.format(value_name))
                self.__add_indent()
                self.__plot_type[plot_kind].append(value_name)
                self.__acf_plot_2d(self.ax[plot_kind][value_name],data[type_dict['x_axis']],data[value_axis],y_error=data[value_axis_error])
                self.ax[plot_kind][value_name].set_xlabel(type_dict['x_axis'])
                self.ax[plot_kind][value_name].set_ylabel(value_name)
                self.__decrease_indent()

            for key in type_dict['With_error_list']:
                value_axis = key
                value_axis_error = 'error_' + key
                value_name = key
                if(len(self.__label) > 0):
                    label = self.__label
                else:
                    label = None
                self.__myprint('[plot : {}]'.format(value_name))
                self.__add_indent()
                self.__plot_type[plot_kind].append(value_name)
                self.__plot_2d(self.ax[plot_kind][value_name],data[type_dict['x_axis']],data[value_axis],y_error=data[value_axis_error],label=label)
                if(label != None):
                    self.ax[plot_kind][value_name].legend(loc="upper right",fontsize=self.basic_size['font'])
                self.ax[plot_kind][value_name].set_xlabel(type_dict['x_axis'])
                self.ax[plot_kind][value_name].set_ylabel(value_name)
                self.__decrease_indent()

            for key in type_dict['Rest_list']:
                value_axis = key
                value_name = key
                if(len(self.__label) > 0):
                    label = self.__label
                else:
                    label = None
                self.__myprint('[plot : {}]'.format(value_name))
                self.__add_indent()
                self.__plot_type[plot_kind].append(value_name)
                self.__plot_2d(self.ax[plot_kind][value_name],data[type_dict['x_axis']],data[value_axis],label=label)
                if(label != None):
                    self.ax[plot_kind][value_name].legend(loc="upper right",fontsize=self.basic_size['font'])
                self.ax[plot_kind][value_name].set_xlabel(type_dict['x_axis'])
                self.ax[plot_kind][value_name].set_ylabel(value_name)
                self.__decrease_indent()

            value_name = 'Energy_totaly_plot'
            for key in type_dict['Energy_list']:
                value_axis = key
                value_axis_error = 'error_' + key
                if(len(self.__label) > 0):
                    label_t = key + ' ' + self.__label
                else:
                    label_t = key
                self.__myprint('[plot : {}]'.format(value_name))
                self.__add_indent()
                self.__plot_type[plot_kind].append(value_name)
                self.__plot_2d(self.ax[plot_kind][value_name],data[type_dict['x_axis']],data[value_axis],y_error=data[value_axis_error],label=label_t)
                self.ax[plot_kind][value_name].set_xlabel(type_dict['x_axis'])
                self.ax[plot_kind][value_name].set_ylabel(value_name)
                self.ax[plot_kind][value_name].legend(loc="upper right",fontsize=self.basic_size['font'])
                self.__decrease_indent()

            for key in self.__plot_type[plot_kind]:
                for key_t in type_dict['Exact_list']:
                    if(('exact_' + key) ==  key_t):
                        value_name = key
                        value_axis = key_t
                        self.__myprint('[plot : {}]'.format(key_t))
                        self.__add_indent()
                        self.__plot_2d(self.ax[plot_kind][value_name],data[type_dict['x_axis']],data[value_axis],label=key_t)
                        self.__decrease_indent()
                        self.ax[plot_kind][value_name].legend(loc="upper right",fontsize=self.basic_size['font'])

            for key in self.ax[plot_kind].keys():
                self.ax['normal'][key].grid(which='both',color='black',linestyle='--')
            self.__decrease_indent()

        self.__myprint('[complete plot : {}]'.format(plot_kind))
        if(plot_value != None):
            self.fig[plot_kind].suptitle('{} '.format(plot_value), fontsize=self.basic_size['font'])
        else:
            self.fig[plot_kind].suptitle('File : {} '.format(file_name), fontsize=self.basic_size['font'])

    def info(self):
        print('[infomation]')
        print('  [self.basic_size] : {}'.format(self.basic_size))
        if(len(self.ax) != 0):
            print('  [self.ax]')
            for key in self.ax.keys():
                for key_t in self.ax[key].keys():
                    print('    [{0} : {1}]  {2}'.format(key, key_t, self.ax[key][key_t]))
        else:
            print('  [ax has no elements yet]')
        if(len(self.fig) != 0):
            print('  [self.fig]')
            for key in self.fig.keys():
                print('    [{0}] {1}'.format(key,self.fig[key]))
        else:
            print('    [fig has no elements yet]')
        if(len(self.__plot_type) != 0):
            print('  [plot_type list]')
            for key in self.__plot_type.keys():
                print('    [{0}] {1}'.format(key,self.__plot_type[key]))
        else:
            print('    [plot_type has no elements yet]')
        self.result_info()

    def help(self):
        print('  [plot_result variables]')
        print('    plot_result(file= string, directory= int, plot_kind= string, plot_value= string,log= bool)')
        print('  [plot_data variables]')
        print('    [Remark : you can overlay some graph on same window until you input fsrplot.show()')
        print('    plot_data(data= data_obtained_by_data_load, data_x= str_or_array_like, data_y= str_or_array_like, data_z= str_or_array_like,') 
        print('                y_error= str_or_array_like, ptype= "2d"_or_"3d", x_axis= str, y_axis= str, z_axis= str, label= str, title= str,') 
        print('                addplot= [plot_kind, value_name], marker=str_matplotlib_form)')
        print('  [Useful axes methods]')
        print('     ax.set_xlim(right=min,left=max)')
        print('     ax.set_ylim(bottom=min,top=max)')
        print('     ax.get_xlim()')
        print('     ax.set_xscale("log")')
        print('     ax.grid(which="both",color="black",linestyle="--")')
        print('     ax.legend(loc="upper right")')
        print('  [IPython useful commands]')
        print('     new line : Ctrl + O') 

    def reload(self,top_directory=None):
        print('[reload result data]') 
        self.__result_whole_info = ''
        self.__result_info = ''
        self.__data_dir_list = []
        self.__variable_params = []
        self.__num_patterns_with_variable_params = []
        self.__common_params = []
        self.__indent = 0
        self.__label = ''
        if(top_directory == None):
            top_directory = self.__top_directory
        else:
            print('[input top_directory : {}]'.format(top_directory))
        self.__set_result_info(top_directory)
        self.info()

    def reset(self,hard=False):
        top_directory = self.__top_directory
        print('[reset : input top_directory : {}]'.format(top_directory))
        if(hard):
            print('[hard reset : remove buffer and reload all data]')
            self.__init__(top_directory=top_directory)
        else:
            self.__plot_kind = ['hist','correlation', 'normal']
            self.ax = {}
            self.fig = {}
            self.__plot_type = {}
            for key in self.__plot_kind:
                self.ax[key] = {}
                self.__plot_type[key] = []
            self.basic_size = {'window_large':20,'window_small':8,'font':20}
            self.__result_whole_info = ''
            self.__result_info = ''
            self.__data_dir_list = []
            self.__variable_params = []
            self.__num_patterns_with_variable_params = []
            self.__common_params = []
            self.__indent = 0
            self.__label = ''
            self.__set_result_info(top_directory)

        self.info()


    def result_info(self,whole_info=False):
        if(whole_info):
            print(self.__result_whole_info)
        else:
            print(self.__result_info)


    def show(self,with_plot=False):
        for key  in self.ax.keys():
            for key_t in self.ax[key].keys():
                del self.ax[key][key_t]
        if(with_plot):
            print('can close by plt_manager.close(fig_target=fig_name)')
            plt.pause(.01)
        else:
            plt.show()


    def close(self,fig_target=None):
        if(fig_target != None):
            plt.close(fig_target)
        else:
            plt.close()


    def dissect_result(self,file=None, directory=None):
        plot_kind = None
        file_name = ''
        directory_name = ''
        directory_name = self.__directory_name_set(file,directory)
        if(file != None):
            self.__myprint('[file name : {}]'.format(file))
            file_name = ''
            file_name = self.__file_name_set(file,directory)
        else:
            self.__myprint('[Error!! : input file name]')
            sys.exit()
        self.__check_json_file(directory_name)
        data, type_dict, plot_kind = self.__data_load(file_name,plot_kind)
        self.__myprint('[check data type list]')
        self.__add_indent()
        for key in type_dict.keys():
            self.__myprint('[{0}] : {1}'.format(key,type_dict[key]))
        self.__decrease_indent()
        self.__myprint('[check data shape]')
        self.__add_indent()
        for key in data.keys():
            self.__myprint('[{0}] : {1}'.format(key,data[key].shape))
        self.__decrease_indent()

    def data_load(self,file=None, directory=None):
        plot_kind = None
        file_name = ''
        directory_name = ''
        directory_name = self.__directory_name_set(file,directory)
        if(file != None):
            self.__myprint('[file name : {}]'.format(file))
            file_name = ''
            file_name = self.__file_name_set(file,directory)
        else:
            self.__myprint('[Error!! : input file name]')
            sys.exit()
        data, type_dict, plot_kind = self.__data_load(file_name,plot_kind)
        self.__myprint('[return values : type_dict, data : type_dict has value names and data is dict type array]')
        self.__myprint('[check data type list]')
        self.__add_indent()
        for key in type_dict.keys():
            self.__myprint('[{0}] : {1}'.format(key,type_dict[key]))
        self.__decrease_indent()
        self.__myprint('[return data]')
        return copy.deepcopy(self.__buffer_data[file_name]['data'])

    def __progress_bar(self,loop,loop_max,add_sentence=None,indent=0):
        sys.stdout.write('\r')
        sentence = ''
        if(indent > 0):
            for i in range(indent):
                sentence += '  ' 
        else:
            for i in range(self.__indent):
                sentence += '  ' 
        progress_ratio = int(float(loop+1)/float(loop_max)*100)
        sentence += '[Progress : {0:0=3}%]'.format(progress_ratio)
        if(add_sentence != None):
            sentence += add_sentence
        sys.stdout.write(sentence)
        sys.stdout.flush()
        if(progress_ratio >= 100):
            sys.stdout.write('\n')

    def __myprint(self,sentence):
        if(not isinstance(sentence, str)):
            sentence = '{}'.format(sentence)
        for i in range(self.__indent):
            sentence = '  ' + sentence
        print(sentence)

    def __add_indent(self,N=0):
        if(N != 0):
            for i in range(N):
                self.__indent += N
        else:
            self.__indent += 1

    def __decrease_indent(self,N=0):
        if(N != 0):
            for i in range(N):
                self.__indent -= N
        else:
            self.__indent -= 1
        if(self.__indent < 0):
            self.__indent = 0

    def __init_indent(self):
        self.__indent = 0

    def __genuine_hist_plot(self,data_range,data_hist,ax,label=None):
        self.__myprint('[geniine hist plot]')
        total_number = np.sum(data_hist)
        n_bin = len(data_range)
        v_max = data_range.max()
        v_min = data_range.min()
        dv = data_range[1] - data_range[0]
        y_value = np.zeros(n_bin)
        normalizer = 0
        for i in range(n_bin):
            normalizer += dv * data_hist[i]
        y_value = data_hist / normalizer 
        if(label == None):
            label = 'unmodify'
        ax.bar(data_range , y_value , width=dv, label=label, alpha=0.4,color='blue')

    def __process_hist_plot(self,data_range,data_hist,ax,n_bin=0,label=None):
        self.__myprint("[modified hist plot]")
        if (n_bin == 0):
            n_bin = 100
        total_number = np.sum(data_hist)
        total_number = int(total_number)
        hist,v_domain,dv= self.__calc_hist(data_range,data_hist,n_bin)
        if(label == None):
            label = 'modify'
        ax.bar(v_domain , hist , width=dv, label=label, alpha=0.4)

    def __exact_gaussian_plot(self,data_range,data_hist,ax,T):
        n_bin = len(data_range)
        total_number = np.sum(data_hist)
        dv = data_range[1] - data_range[0]
        v_max = data_range.max()
        v_min = data_range.min()
        variance = 0
        mean = 0
        y_value = np.zeros(n_bin)
        normalizer = 0
        for i in range(n_bin):
            normalizer += dv * data_hist[i]
        y_value = data_hist[:] / normalizer
        for i in range(n_bin):
            variance += y_value[i] * data_hist[i] * data_hist[i] * dv;
            mean += y_value[i] * data_hist[i] * dv;
        variance = variance - mean * mean 
        sigma = np.sqrt(T)
        v = np.linspace(v_min,v_max,n_bin)
        Gaussian = norm.pdf(v,loc=0.0,scale=sigma)
        error = np.sqrt(variance / (total_number + 1))
        self.__add_indent()
        self.__myprint("[mean : {0}, variance :  {1}, error : {2}]".format(mean, variance, error))
        self.__decrease_indent()
        ax.plot(v,Gaussian,label='Gaussian:T={0:.3g}'.format(T))

    def __hist_plot_overlaid(self,data_range,data_hist,data_domain,ax,n_bin=0,N_plot=0,label=None):
        self.__myprint('[modified hist plot 2d overlaid]')
        self.__add_indent()
        if(N_plot ==0 or len(data_domain) < N_plot):
            N_plot = len(data_domain)
            loop_max = int(len(data_domain))
        else:
            loop_max = N_plot
        if(n_bin==0):
            n_bin = len(data_range[:,0])
            self.__myprint('[set n_bin : {}]'.format(n_bin))
        else:
            self.__myprint('[n_bin input :{}]'.format(n_bin))
        self.__myprint('[set loop_max : {}]'.format(loop_max))
        t_max = data_domain.max()
        for loop_t in range(loop_max):
            loop = loop_t * int(len(data_domain)/loop_max)
            hist,v_domain,dv= self.__calc_hist(data_range[:,loop],data_hist[:,loop],n_bin)
            print_sentence = '[ d_range : {0:.4e}, numeric d_range : {1:.4e}]'.format( dv, data_range[1,0] - data_range[0,0])
            if(loop_max < 15):
                ax.bar(v_domain , hist , width=dv, color=cm.jet(data_domain[loop]/t_max), alpha=0.2, label='{0} : {1}'.format(label,data_domain[loop]))
            else:
                ax.bar(v_domain , hist , width=dv, color=cm.jet(data_domain[loop]/t_max), alpha=0.2)
            self.__progress_bar(loop_t,loop_max,add_sentence=print_sentence)
        if(loop_max < 15):
            ax.legend(loc="upper right",prop = {'size':self.basic_size['font']})
        self.__decrease_indent()

    def __hist_plot_3d(self,data_range,data_hist,data_domain,ax,n_bin=0,N_plot=0):
        self.__myprint('[modified hist plot 3d]')
        self.__add_indent()
        if(N_plot ==0 or len(data_domain) < N_plot):
            N_plot = len(data_domain)
            loop_max = int(len(data_domain))
        else:
            loop_max = N_plot
        if(n_bin == 0):
            n_bin = len(data_range[:,0])
            self.__myprint('[set n_bin : {}]'.format(n_bin))
        else:
            self.__myprint('[n_bin input :{}]'.format(n_bin))
        self.__myprint('[set loop_max : {}]'.format(loop_max))
        t_max = data_domain.max()
        for loop_t in range(loop_max):
            loop = loop_t * int(len(data_domain)/loop_max)
            hist,v_domain,dv= self.__calc_hist(data_range[:,loop],data_hist[:,loop],n_bin)
            print_sentence = '[ d_range : {0:.4e}, numeric d_range : {1:.4e}]'.format( dv, data_range[1,0] - data_range[0,0])
            ax.bar(v_domain , hist, data_domain[loop], zdir='y', width=dv, color=cm.jet(data_domain[loop]/t_max), alpha=0.5)
            self.__progress_bar(loop_t,loop_max,add_sentence=print_sentence)
        self.__decrease_indent()

    def __calc_hist(self,data_range,data_hist,n_bin):
        length = len(data_range)
        v_max = data_range.max()
        v_min = data_range.min()
        dv = np.float64((v_max - v_min)/np.float64(n_bin-1))
        hist = np.zeros(n_bin)
        v_domain = np.zeros(n_bin)
        if(n_bin >= length):
            diff = 1
        elif(n_bin == 0):
            diff = 1
        else:
            diff = length // n_bin
    
        if((length % n_bin) >= 0.5):
            diff +=1
        for i in range(length):
            count = i // diff;
            hist[count] += data_hist[i]
        normalizer = 0
        for i in range(n_bin):
            normalizer += dv * hist[i]
        hist = hist / normalizer 
        for i in range(n_bin):
            v_domain[i] = v_min + dv *np.float64(i) 
        return copy.deepcopy(hist),copy.deepcopy(v_domain),dv

    def __plot_3d(self,ax,data_range,data_z,data_domain,N_plot=0):
        self.__add_indent()
        if(N_plot ==0 or len(data_domain) < N_plot):
            N_plot = len(data_domain)
            loop_max = int(len(data_domain))
        else:
            loop_max = N_plot
        x, y = np.meshgrid(data_range,data_domain,indexing='xy')
        for loop_t in range(loop_max):
            loop = loop_t * int(len(data_domain)/loop_max)
            ax.plot(x[loop,:],y[loop,:],data_z[:,loop],color=cm.jet(data_domain[loop]/data_domain.max()))
            self.__progress_bar(loop_t,loop_max)
        self.__decrease_indent()

    def __plot_2d_overlaid(self,data_range,data_z,data_domain,ax,N_plot=0,label=None):
        self.__add_indent()
        if(N_plot ==0 or len(data_domain) < N_plot):
            N_plot = len(data_domain)
            loop_max = int(len(data_domain))
        else:
            loop_max = N_plot
        for loop_t in range(loop_max):
            loop = loop_t * int(len(data_domain)/loop_max)
            if(loop_max < 15):
                ax.plot(data_range,data_z[:,loop],color=cm.jet(data_domain[loop]/data_domain.max()),label='{0} : {1}'.format(label,data_domain[loop]))
            else:
                ax.plot(data_range,data_z[:,loop],color=cm.jet(data_domain[loop]/data_domain.max()))
            self.__progress_bar(loop_t,loop_max)
        if(loop_max < 15):
            ax.legend(loc="upper right",prop = {'size':self.basic_size['font']})
        self.__decrease_indent()

    def __acf_plot_2d(self,ax,x,y,y_error=None,label=None):
        vv = y[0]
        y_t = y / vv
        if(isinstance(y_error,list)):
            ax.plot(x,y_t,label=label)
        else:
            if(isinstance(label,str)):
                ax.errorbar(x,y_t,yerr=y_error,label=label)
            else:
                ax.errorbar(x,y_t,yerr=y_error)

    def __plot_2d(self,ax,x,y,y_error=None,label=None,color=None,marker=None,log_scale=False):
        if(marker is None):
            marker = ''
        if(y_error is None):
            if(isinstance(label,basestring)):
                ax.plot(x,y,label=label,color=color,marker=marker)
            else:
                ax.plot(x,y,color=color,marker=marker)
        else:
            marker = 'x'
            if(isinstance(label,basestring)):
                ax.errorbar(x,y,yerr=y_error,label=label,color=color,marker=marker)
            else:
                ax.errorbar(x,y,yerr=y_error,color=color,marker=marker)
        if(log_scale):
            ax.set_yscale('log')  
            ax.set_xscale('log')  
