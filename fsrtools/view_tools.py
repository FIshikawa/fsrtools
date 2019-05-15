import sys
import os
import json
import copy
import datetime
import math
import numpy as np
from scipy import stats
from scipy.stats import norm
from scipy.stats import cauchy
from matplotlib import cm
import matplotlib.pyplot as plt 
import matplotlib.ticker as ptick
from mpl_toolkits.mplot3d import axes3d
from fsrtools.util import LogManager
from fsrtools.util import colors
from fsrtools.simulate_tools import set_total_combinations

class PlotManager:
    def __init__(self,top_directory=None,file=None):
        self._plot_type_list = ['hist','correlation','3d','normal','totally']
        self.ax = {}
        self.fig = {}
        self._plot_type = {}
        for key in self._plot_type_list:
            self.ax[key] = {}
            self._plot_type[key] = []
        self.basic_size = {'window_large':20,'window_small':8,'font':20}
        self._label = ''
        self._buffer_data = {}
        self._top_directory = ''
        self._result_data_map = []
        self._config_data_map= []
        self._myprint = LogManager(cout_tag=True)

        if(top_directory):
            self._top_directory = os.path.normpath(top_directory)
            self._config_data_map, self._result_data_map  = set_data_map(top_directory)
        if(file):
            top_directory = self._directory_name_set(file_path=file)
            self._top_directory = os.path.normpath(top_directory)
            file_in_dir_name = os.path.dirname(file)
            self._config_data_map, self._result_data_map  = set_data_map(top_directory)

    def result_info(self,whole_info=False):
        if(whole_info):
            print('[result whole info]')
            top_depth = len(os.path.normpath(self._top_directory).split('/'))
            for current_directory, included_directory, files in os.walk(self._top_directory):
                self._myprint.reset_indent()
                indent_length = len(current_directory.split('/'))
                self._myprint.add_indent(indent_length - top_depth)
                self._myprint(current_directory)
                if(files):
                    self._myprint('{}'.format(files))
            self._myprint.reset_indent()
        else:
            print('[result info]')
            log_write = LogManager(cout_tag=True)
            log_write.add_indent()
            counter = 0
            if(self._config_data_map):
                for i, element in enumerate(self._config_data_map):
                    log_write(colors('GREEN') + '[experiment date : {}]'.format(element['common_directory']) + colors('END'))
                    log_write.add_indent()
                    if(element['variable_parameters']):
                        log_write('[common parameters] : ',end='')
                        for key, value in element['common_parameters'].items():
                            log_write('{0} : {1}, '.format(key, value),end='')
                        log_write('')
                        log_write.add_indent()
                        for result_data in self._result_data_map:
                            if(result_data['common_parameter_number'] == i):
                                counter += 1
                                log_write('[{}] '.format(counter),end='')
                                for key, value in result_data['variable_parameters'].items():
                                    log_write('{0} : {1} '.format(key,value),end='') 
                                log_write('')
                                log_write.add_indent()
                                log_write('[files] : {}'.format(result_data['files']))
                                log_write.decrease_indent()
                        log_write.decrease_indent()
                    log_write.decrease_indent()
                log_write.decrease_indent()
            else:
                for i, element in enumerate(self._result_data_map):
                    log_write('[{0}][directory] : {1}'.format(i+1,element['directory']))
                    log_write.add_indent()
                    log_write('[files] : {} '.format(element['files']))
                    log_write.decrease_indent()

    def info(self):
        print('[infomation]')
        print('  [self.basic_size] : {}'.format(self.basic_size))
        if(self.ax):
            print('  [self.ax]')
            for key in self.ax.keys():
                for key_t in self.ax[key].keys():
                    print('    [{0} : {1}]  {2}'.format(key, key_t, self.ax[key][key_t]))
        else:
            print('  [ax has no elements yet]')
        if(self.fig):
            print('  [self.fig]')
            for key in self.fig.keys():
                print('    [{0}] {1}'.format(key,self.fig[key]))
        else:
            print('    [fig has no elements yet]')
        if(self._plot_type):
            print('  [plot_type list]')
            for key in self._plot_type.keys():
                print('    [{0}] {1}'.format(key,self._plot_type[key]))
        else:
            print('    [plot_type has no elements yet]')
        self.result_info()

    def help(self):
        print('  [plot_result variables]')
        print('    plot_result(file= string, directory= int, plot_type= string, plot_value= string, log_scale= bool, silent= bool)')
        print('  [plot_data variables]')
        print('    [Remark : you can overlay some graph on same window until you input fsrplot.show()')
        print('    plot_data(data= data_obtained_by_data_load, data_x= str_or_array_like, data_y= str_or_array_like, data_z= str_or_array_like,') 
        print('                y_error= str_or_array_like, ptype= "2d"_or_"3d", x_axis= str, y_axis= str, z_axis= str, label= str, title= str,') 
        print('                addplot= [plot_type, value_name], marker=str_matplotlib_form)')
        print('  [whole result data can be accessed by result_data_map method function]')
        print('     dictionary_type_data = fsrplot.result_data_map()')
        print('     result_data_map is a dictionary : the order corresponds to the number veiwed by result_info')
        print('  [Useful axes methods]')
        print('     ax.set_xlim(right=min,left=max)')
        print('     ax.set_ylim(bottom=min,top=max)')
        print('     ax.get_xlim()')
        print('     ax.set_xscale("log")')
        print('     ax.grid(which="both",color="black",linestyle="--")')
        print('     ax.legend(loc="upper right")')
        print('  [IPython useful commands]')
        print('     new line : Ctrl + O') 

    def result_data_map(self):
        result_data_map_total = {}
        for i, result_data in enumerate(self._result_data_map):
            result_data_map_total[i+1] = result_data
            result_data_map_total[i+1]['common_parameters'] = copy.deepcopy(self._config_data_map[result_data['common_parameter_number']]['common_parameters'])
        return result_data_map_total

    def result_data_map_all(self):
        result_data_map_total = self.result_data_map()
        for key, result_data in result_data_map_total.items():
            result_file_detail = {}
            for file_name in result_data['files']:
                if('result' in file_name):
                    file_path = os.path.join(result_data['directory'],file_name)
                    data, type_dict, plot_type = self._data_load(file_path)
                    result_file_detail[file_name] = {'value_list':type_dict,'plot_type':plot_type}
            result_data_map_total[key]['result_file_detail'] = result_file_detail
        return result_data_map_total

    def reload(self,top_directory=None):
        print('[reload result data]') 
        self._label = ''
        if(top_directory is not None):
            top_directory = self._top_directory
        else:
            print('[input top_directory : {}]'.format(top_directory))
        self._init_(top_directory=top_directory)
        self.info()

    def reset(self,hard=False):
        print('[reset attributes]')
        if(hard):
            print('[hard reset : remove buffer and reload all data]')
            top_directory = self._top_directory
            self._init_(top_directory=top_directory)
        else:
            self._plot_type_list = ['hist','correlation','3d','normal','totally']
            self.ax = {}
            self.fig = {}
            self._plot_type = {}
            for key in self._plot_type_list:
                self.ax[key] = {}
                self._plot_type[key] = []
            self.basic_size = {'window_large':20,'window_small':8,'font':20}
            self._label = ''
        self.info()

    def show(self,with_plot=False):
        if(with_plot):
            print('can close by plt_manager.close(fig_target=fig_name)')
            plt.pause(.01)
        else:
            plt.show()
            for key in self._plot_type_list:
                self.ax[key] = {}
                self._plot_type[key] = []
                self._label = ''

    def close(self,fig_target=None):
        if(fig_target != None):
            plt.close(fig_target)
        else:
            plt.close()

    def data_load(self,file=None, directory=None, plot_type=None,silent=False):
        file_path = ''
        if(file is not None):
            file_path = ''
            if(directory is not None):
                file_path = self._file_path_set(file,directory)
            else:
                file_path = file
        else:
            raise KeyError('no input file name')
        if(not file_path in self._buffer_data.keys()):
            data, type_dict, plot_type = self._data_load(file_path,plot_type,silent=silent)
        else:
            data      = copy.deepcopy(self._buffer_data[file_path]['data'])
            type_dict = copy.deepcopy(self._buffer_data[file_path]['type_dict'])
            plot_type = copy.deepcopy(self._buffer_data[file_path]['plot_type'])
        if(not silent):
            self._myprint('[data type list]')
            self._myprint.add_indent()
            for key in type_dict.keys():
                self._myprint('[{0}] : {1}'.format(key,type_dict[key]))
            self._myprint.decrease_indent()
        return data, type_dict, plot_type

    def time_result(self):
        print('return time results and parameter data')
        time_data = {}
        parameter_data = {}
        for i, result_data in enumerate(self._result_data_map):
            if('duration' in result_data['time_info'] and not 'remark' in result_data['time_info']):
                time_data[i] = result_data['time_info']['duration']
                parameter_data[i] = result_data['variable_parameters']
            else:
                print('[{}-th result is failed simulation : no time result]'.format(i))
        return parameter_data, time_data

    def plot_result(self,file=None,directory=None,plot_type=None,plot_value=None,save_fig=False,N_plot=None,log_scale=False,label=None,label_position=None,silent=False):
        if(silent):
            self._myprint = LogManager(silent=silent)
        else:
            self._myprint.reset_indent()
        directory_name = '' 
        file_path = ''
        result_files = []
        if(file is not None):
            if(isinstance(directory, list)):
                self._myprint('[dictionary list input : overlaide plot mode]')
                if(plot_value):
                    for directory_each in directory:
                        file_path = self._file_path_set(file,directory_each)
                        if(not os.path.exists(file_path)):
                            raise NameError('{} does not exist'.format(file_path)) 
                        directory_name = self._directory_name_set(file_path=file_path)
                        json_data = self._check_json_file(directory_name)
                        if(json_data is None and plot_type is None):
                            raise KeyError('must select plot_type')
                        else:
                            self._plot_file(file_path,directory_each,json_data,plot_type=plot_type,plot_value=plot_value,log_scale=log_scale,label=label,N_plot=N_plot)  
                            if(label_position is not None):
                                for plot_type_temp in self.ax.keys():
                                    for plot_value_temp in self.ax[plot_type_temp].keys():
                                        self.ax[plot_type_temp][plot_value_temp].legend(loc=label_position,prop = {'size':self.basic_size['font']})
                else:
                    raise KeyError('no plot_value expeceted : plot value should be input')
            else:
                self._myprint('[file plot mode]')
                self._myprint('[file name : {}]'.format(file))
                if(directory is not None):
                    file_path = self._file_path_set(file,directory)
                else:
                    file_path = file
                if(not os.path.exists(file_path)):
                    raise NameError('{} does not exist'.format(file_path)) 
                directory_name = self._directory_name_set(file_path=file_path)
                json_data = self._check_json_file(directory_name)
                self._myprint.add_indent()
                if(json_data is None and plot_type is None):
                    raise KeyError('must select plot_type')
                self._plot_file(file_path,directory,json_data,plot_type=plot_type,plot_value=plot_value,log_scale=log_scale,label=label,N_plot=N_plot)  
                if(label_position is not None):
                    for plot_type_temp in self.ax.keys():
                        for plot_value_temp in self.ax[plot_type_temp].keys():
                            self.ax[plot_type_temp][plot_value_temp].legend(loc=label_position,prop = {'size':self.basic_size['font']})
                if(save_fig):
                    fig_name = os.path.basename(file_path)
                    fig_name = os.path.join(directory_name,fig_name.split('.')[0] + '.pdf')
                    self._myprint('[save figure : {}]'.format(fig_name))
                    plt.savefig(fig_name,format='pdf')
        elif(file is None and directory is not None):
            directory_name = self._directory_name_set(directory=directory)
            self._myprint('[directory plot mode : plot all "result" files" in {}]'.format(directory_name))
            files_in_dir = os.listdir(directory_name)
            self._myprint('[check files in the directory]')
            self._myprint.add_indent()
            self._myprint(files_in_dir)
            self._myprint.decrease_indent()
            json_data = self._check_json_file(directory_name)
            for key in files_in_dir:
                if('result' in key):
                    result_files.append(key)
            if(not result_files):
                raise ValueError('result directory "{}" have no results'.format(directory_name))
            self._myprint.add_indent()
            self._myprint('[plot "result" files s.t]')
            self._myprint('  {}'.format(result_files))
            self._myprint.decrease_indent()
            self._myprint.add_indent()
            self._myprint('[start ploting]')
            for key in result_files:
                self._plot_file(os.path.join(directory_name,key),directory,json_data,plot_type=plot_type,log_scale=log_scale,N_plot=N_plot)
                if(save_fig):
                    fig_name = os.path.join(directory_name, key.split('.')[0] + '.pdf')
                    self._myprint('[save figure : {}]'.format(fig_name))
                    plt.savefig(fig_name,format='pdf')
        else:
            raise KeyError('no selected direcotry or result file')
        self._myprint.decrease_indent()
        self._myprint('[plot completed]')
        self._myprint = LogManager(cout_tag=True)

    def plot_data(self,data=None,data_x=None,data_y=None,data_z=None,y_error=None,ptype=None,x_axis=None,y_axis=None,z_axis=None,label=None,title=None,addplot=None,x_lim=None,y_lim=None,marker=None):
        if(addplot is not None and isinstance(addplot,list)):
            plot_type = addplot[0]
            value_name = addplot[1]
            if(not plot_type in self.fig.keys() or not value_name in self.ax[plot_type].keys()):
                raise NameError('target result does not exist')
        else:
            plot_type= 'temporary'
            value_name = 'temporary'
        data_list = []
        data_dict = {}
        axis_list = []
        data_list.extend([data_x,data_y,data_z,y_error])
        axis_list.extend([x_axis,y_axis,z_axis])
        if(ptype == '2d'):
            if(not plot_type in self.fig.keys() or not value_name in self.ax[plot_type].keys()):
                self.ax[plot_type] = {}
                self.fig[plot_type], self.ax[plot_type][value_name] = plt.subplots(figsize=(self.basic_size['window_small']*1.618,self.basic_size['window_small']))
                self._myprint('[Remark : fig and ax key of plot_data is "temporary"]')
                self._myprint('[You can overlay some graph on same window which is identified by the key "temporary"]')
        else:
            if((len([x for x in axis_list if x != None]) + (1 if title != None else 0)) < 1 and len([x for x in data_list if x != None]) > 0): 
                raise KeyError('ptype must be chosen from "2d" or "3d"')
        if(data is None and ptype is not None):
            self._plot_2d(self.ax[plot_type][value_name],data_x,data_y,y_error=y_error,label=label,marker=marker)
        elif(isinstance(data,dict) and ptype is not None):
            for i in range(4):
                if(data_list[i] is not None):
                    if(not isinstance(data_list[i],str)):
                        self._myprint('[Error! : data_xyz, y_error shold be str]') 
                        sys.exit()
                    else:
                        if(data_list[i] in data.keys()):
                            data_dict[i] = data[data_list[i]]
                        else:
                            raise KeyError('{} is not in data'.format(data_list[i])) 
                else:
                    data_dict[i] = None
            if(axis_list[0] is None):
                self.ax[plot_type][value_name].set_xlabel(data_list[0])
            if(axis_list[1] is None):
                self.ax[plot_type][value_name].set_ylabel(data_list[1])
            self._plot_2d(self.ax[plot_type][value_name],data_dict[0],data_dict[1],y_error=data_dict[3],label=label,marker=marker)
        if(isinstance(x_lim,dict)):
            self.ax[plot_type][value_name].set_xlim(left=x_lim[0],right=x_lim[1])
        if(isinstance(y_lim,dict)):
            self.ax[plot_type][value_name].set_ylim(bottom=y_lim[0],top=y_lim[1])
        if(label is not None):
            self.ax[plot_type][value_name].legend(loc="upper right",fontsize=self.basic_size['font'])
        if(title is not None):
            self.ax[plot_type][value_name].set_title(title)
        for key in [x for x in axis_list if x != None]:
            if(not isinstance(key,str)):
                self._myprint('[Error! : xyz_axis shold be str]') 
            else:
                if(axis_list.index(key) == 0):
                    self.ax[plot_type][value_name].set_xlabel(key)
                elif(axis_list.index(key) == 1):
                    self.ax[plot_type][value_name].set_ylabel(key)
                elif(axis_list.index(key) == 2):
                    self.ax[plot_type][value_name].set_zlabel(key)

    def _directory_name_set(self,file_path=None,directory=None):
        directory_name = ''
        if(file_path is not None):
            if(isinstance(file_path, str)):
                file_path = os.path.normpath(file_path)
                directory_name = os.path.dirname(file_path)
                if(not directory_name):
                    directory_name = os.getcwd()
        elif(directory is not None):
            if(isinstance(directory, int)): 
                directory_name = self._result_data_map[directory-1]['directory']
            else:
                directory_name = directory
        else:
            raise ValueError('no file or directory input')
        return directory_name

    def _file_path_set(self,file,directory):
        file_path = ''
        if(isinstance(directory,int)):
            directory_name = self._result_data_map[directory-1]['directory']
        else:
            directory_name = directory
        file_path = os.path.join(directory_name, file)
        return file_path 

    def _check_json_file(self,directory_name):
        json_file_name = ''
        files_in_dir = os.listdir(directory_name)
        for key in files_in_dir:
            if('.json' in key):
                json_file_name = key 
                break
        if(not json_file_name):
            self._myprint('[cannot find parameter file : unset parameter file mode]')
            return None
        else:
            json_file_name =  os.path.join(directory_name,json_file_name)
            self._myprint('[read parameter : {}]'.format(json_file_name))
            json_data = json.load(open(json_file_name,'r'))
            for key in json_data.keys():
                self._myprint('  [{0} : {1} ]'.format(key,json_data[key]))
            return json_data

    def _data_load(self,file_path,plot_type=None,silent=False):
        type_dict = {}
        data = {}
        myprint_temp = copy.deepcopy(self._myprint)
        if(silent):
            self._myprint = LogManager(silent=silent)
        if(plot_type):
            if(not plot_type in self._plot_type_list):
                raise KeyError('input plot_type is not in our set')
            else:
                self._myprint('[input plot_type : {}]'.format(plot_type))
        else:
            self._myprint('[plot_type is not input : automatically set]')
            for key in self._plot_type_list:
                if(key in file_path):
                    plot_type = key
                    self._myprint('[set plot_type {} : {} in the result file name]'.format(plot_type,plot_type))
            if(plot_type is None):
                self._myprint('[normal plot data]')
                plot_type = 'normal'

        data_raw = np.loadtxt(file_path, dtype = np.float64,skiprows=1)
        data_file = open(file_path,'r')

        if(plot_type == 'normal'):
            type_dict = {'ACF_list' : [],
                         'With_error_list' : [],
                         'Energy_list' : [],
                         'Rest_list' : [],
                         'Exact_list' : [],
                         'x_axis' : ''}
            value_keys = data_file.readline()
            value_keys = value_keys.strip().split(' ')
            value_keys.pop(0)
            data[value_keys[0]] = data_raw[:,0]
            type_dict['x_axis'] = value_keys[0]
            for key in value_keys[1:]:
                data[key] = data_raw[:,value_keys.index(key)]
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

        elif(plot_type in ['hist','correlation','3d']):
            x_data = data_file.readline()
            x_data = x_data.strip()
            x_data = x_data.split(' ')
            x_data.pop(0)
            data[x_data[0]] = np.zeros(len(x_data[1:]))
            for i in range(len(x_data[1:])):
                data[x_data[0]][i] = x_data[1+i]
            value_keys = data_file.readline()
            value_keys = value_keys.strip()
            value_keys = value_keys.split(' ')
            value_keys.pop(0)

            if(plot_type == 'hist'):
                type_dict = { 'y_axis' : '',
                              'values' : [],
                              '3d_plot':[],
                              '2d_plot':[]}
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
                    data[key]['range'] = data_raw[:,[x for x in range(len(value_keys)) if 'range' in value_keys[x] and key in value_keys[x]]]
                    data[key]['hist'] = data_raw[:,[x for x in range(len(value_keys)) if 'hist' in value_keys[x] and key in value_keys[x]]]

            elif(plot_type in ['correlation','3d']):
                type_dict = { 'y_axis' : '',
                              'x_axis' : '',
                              'values' : [],
                              '3d_plot':[],
                              '2d_plot':[]}
                type_dict['y_axis'] = x_data[0]
                type_dict['x_axis'] = value_keys[0]
                data[value_keys[0]] = data_raw[:,0]
                type_dict['values'].append(value_keys[1])
                for key_t in value_keys[1:]:
                    if(not key_t in type_dict['values']):
                        type_dict['values'].append(key_t)
                for key in type_dict['values']:
                    type_dict['3d_plot'].append(key + '_3d_plot')
                    type_dict['2d_plot'].append(key + '_2d_plot')
                    data[key] = data_raw[:,[x for x in range(len(value_keys)) if key in value_keys[x]]]
            else:
                raise KeyError('input plot_type is not expeceted')

        elif(plot_type == 'totally'):
            type_dict = {'y_list' : [],
                         'x_axis' : ''}
            value_keys = data_file.readline()
            value_keys = value_keys.strip()
            value_keys = value_keys.split(' ')
            value_keys.pop(0)
            data[value_keys[0]] = data_raw[:,0]
            type_dict['x_axis'] = value_keys[0]
            for key in value_keys[1:]:
                data[key] = data_raw[:,value_keys.index(key)]
                type_dict['y_list'].append(key)
        self._myprint = myprint_temp
        return data, type_dict, plot_type

    def _set_fig_ax(self,type_dict,plot_type,plot_value=None,directory=None,label=None):
        self._myprint('[set fig and ax]')
        self._myprint.add_indent()
        total_number_of_plot = 0

        if(plot_value is None and plot_type != 'totally'):
            if(plot_type == 'normal'):
                total_number_of_plot = len(type_dict['ACF_list']) \
                                        + len(type_dict['With_error_list']) \
                                        +  len(type_dict['Rest_list'])\
                                        + (1 if len(type_dict['Energy_list']) > 0 else 0) 
            
            elif(plot_type in ['hist','correlation','3d']):
                total_number_of_plot = len(type_dict['3d_plot']) + len(type_dict['2d_plot']) 
            elif(plot_type == 'totally'):
                total_number_of_plot = 1
            self._myprint('[total number of plot : {}]'.format(total_number_of_plot))
            if(total_number_of_plot != 1):
                self.fig[plot_type] = plt.figure(figsize=(self.basic_size['window_large']*1.618,self.basic_size['window_large']))
                self.fig[plot_type].subplots_adjust(left=0.075, bottom=0.05, right=0.95, top=0.95, wspace=0.15, hspace=0.15)
                if((total_number_of_plot % 3) == 0):
                    vertical_length = 3
                    horizontal_length = int(total_number_of_plot / vertical_length) 
                elif((total_number_of_plot % 2) == 0):
                    vertical_length = 2
                    horizontal_length = int(total_number_of_plot / vertical_length) 
                else:
                    vertical_length = 3
                    horizontal_length = int(total_number_of_plot / vertical_length) + 1
                if(plot_type == 'normal'):
                    counter = 1
                    for key_t in ['ACF_list','With_error_list','Rest_list']:
                        for key in type_dict[key_t]:
                            self.ax[plot_type][key] = self.fig[plot_type].add_subplot(vertical_length, horizontal_length,counter)
                            counter += 1
                    if(len(type_dict['Energy_list']) > 0):
                        value_name = 'Energy_totaly_plot'
                        self.ax[plot_type][value_name] = self.fig[plot_type].add_subplot(vertical_length, horizontal_length,counter)
                elif(plot_type in ['hist','correlation','3d']):
                    counter = 1
                    for key in type_dict['2d_plot']:
                        self.ax[plot_type][key] = self.fig[plot_type].add_subplot(vertical_length, horizontal_length,counter)
                        counter += 1
                    for key in type_dict['3d_plot']:
                        self.ax[plot_type][key] = self.fig[plot_type].add_subplot(vertical_length, horizontal_length,counter,projection='3d')
                        counter += 1
            else:
                finite_key = [value for key, value in type_dict.items() if len(value) > 0]
                finite_key = finite_key[0][0]
                self.fig[plot_type], self.ax[plot_type][finite_key] = plt.subplots(figsize=\
                                                                                    (self.basic_size['window_small']*1.618*1.5,\
                                                                                     self.basic_size['window_small']*1.5))
        elif(plot_type == 'totally'):
            plot_value = 'Totally_plot'
            self.fig[plot_type], self.ax[plot_type][plot_value] = plt.subplots(figsize=\
                                                                                (self.basic_size['window_small']*1.618*1.5,\
                                                                                 self.basic_size['window_small']*1.5))
        else:
            self._myprint('[plot_value is input : {}]'.format(plot_value))
            self._myprint('[plot_type  is input : {}]'.format(plot_type))
            check_list = []
            if(plot_type == 'normal'):
                check_list.extend([x for x in type_dict.keys() if x != 'Energy_list' and x != 'x_axis']) 
            elif(plot_type in ['correlation','3d,','hist']):
                check_list.extend([x for x in type_dict.keys() if x != 'y_axis' and x != 'x_axis' and x != 'values']) 

            for key in check_list:
                if(plot_value in type_dict[key]): 
                    self._myprint('[detect : plot_value in : {}]'.format(key))
                    del type_dict[key][:]
                    type_dict[key].append(plot_value)
                    if(plot_value in self.ax[plot_type].keys()):
                        self._myprint('[{} is already set in {} plots : added into target plot]'.format(plot_value,plot_type))
                    else:
                        self._myprint('[plot_value is not in axes keys : create]')
                        self.fig[plot_type], self.ax[plot_type][plot_value] = plt.subplots(figsize=\
                                                                                        (self.basic_size['window_small']*1.618,\
                                                                                            self.basic_size['window_small']))
                else:
                    del type_dict[key][:]

            if(plot_type == 'normal'):
                if(plot_value == 'Energy_totally_plot'):
                    if(plot_value in self.ax[plot_type].keys()):
                        self._myprint('[{} is already set in {} plots : added into target plot]'.format(plot_value,plot_type))
                    else:
                        self._myprint('[plot_value is not in axes keys : create]')
                        self.fig[plot_type], self.ax[plot_type][plot_value] = plt.subplots(figsize=\
                                                                                           (self.basic_size['window_small']*1.618,\
                                                                                               self.basic_size['window_small']))
                else:
                    del type_dict['Energy_list'][:]

            if(len([x for x in check_list if len(type_dict[x]) > 0]) < 1):
                raise KeyError('{} is not in {} plots'.format(plot_value,plot_type))

            self._label = ''
            if(label is not None):
                if(label):
                    self._myprint('[label detect : {}]'.format(label))
                    if(isinstance(label,list)):
                        for label_each in label:
                            self._label += '{0} : {1}, '.format(label_each, self._result_data_map[directory-1]['parameters'][label_each])
                    else:
                        self._label = '{0} : {1}, '.format(label, self._result_data_map[directory-1]['parameters'][label])
                else:
                    self._label = ''
            else:
                for key, value in self._result_data_map[directory-1]['variable_parameters'].items():
                    self._label += '{0} : {1}, '.format(key, value)

        self._myprint.decrease_indent()

    def _plot_file(self,file_path,directory,params_dict=None,plot_type=None,plot_value=None,log_scale=False,label=None,N_plot=None):
        plt.rcParams["font.size"] = self.basic_size['font']
        if(N_plot is None):
            N_plot = 10
        if(params_dict != None):
            if('T' in params_dict.keys()):
                T = params_dict['T']
            if('t' in params_dict.keys() and 'N_time' in params_dict.keys()):
                dt = params_dict['t'] / float(params_dict['N_time'])
            if('t' in params_dict.keys()):
                t = params_dict['t']
            if('N_time_resolve' in params_dict.keys()):
                N_time_resolve = params_dict['N_time_resolve']

        data, type_dict, plot_type = self.data_load(file=file_path,plot_type=plot_type)

        if(plot_type == 'hist'):
            self._myprint('[hist plot]')
            del self._plot_type[plot_type][:]
            self._myprint.add_indent()
            self._set_fig_ax(type_dict,plot_type,plot_value=plot_value,directory=directory,label=label)

            for key in type_dict['2d_plot']:
                for value_name in type_dict['values']:
                    if(value_name in key):
                        self._myprint('[plot : {}]'.format(key))
                        self._myprint.add_indent()
                        self._plot_type[plot_type].append(key)
                        if('head' in key or 'tail' in key):
                            axis_num = (0 if 'head' in key else -1)
                            self._genuine_hist_plot(
                                                    data[value_name]['range'][:,axis_num],
                                                    data[value_name]['hist'][:,axis_num],
                                                    self.ax[plot_type][key]
                                                    )
                            self._process_hist_plot(
                                                    data[value_name]['range'][:,axis_num],
                                                    data[value_name]['hist'][:,axis_num],
                                                    self.ax[plot_type][key]
                                                    )
                            if('Velocity' in key):
                                if(type_dict['y_axis'] in ['T','Temperture','temperture']):
                                    if('head' in key):
                                        self._exact_gaussian_plot(
                                                                  data[value_name]['range'][:,axis_num],
                                                                  data[value_name]['hist'][:,axis_num],
                                                                  self.ax[plot_type][key],
                                                                  data[type_dict['y_axis']][0]
                                                                  )
                                    else:
                                        self._exact_gaussian_plot(
                                                                  data[value_name]['range'][:,axis_num],
                                                                  data[value_name]['hist'][:,axis_num],
                                                                  self.ax[plot_type][key],
                                                                  data[type_dict['y_axis']][-1]
                                                                  )
                            self.ax[plot_type][key].legend(loc="upper right",prop = {'size':self.basic_size['font']})
                        else:
                            self._hist_plot_overlaid(
                                                     data[value_name]['range'],
                                                     data[value_name]['hist'],
                                                     data[type_dict['y_axis']],
                                                     self.ax[plot_type][key],
                                                     N_plot=N_plot,
                                                     label=type_dict['y_axis']
                                                     )
                        self.ax[plot_type][key].set_title(key)
                        self.ax[plot_type][key].set_xlabel(value_name)
                        self.ax[plot_type][key].set_ylabel('{} Distribution'.format(value_name))
                        self._myprint.decrease_indent()

            for key in type_dict['3d_plot']:
                for value_name in type_dict['values']:
                    if(value_name in key):
                        self._myprint('[plot : {}]'.format(key))
                        self._myprint.add_indent()
                        self._plot_type[plot_type].append(key)
                        self._hist_plot_3d(
                                           data[value_name]['range'],
                                           data[value_name]['hist'],
                                           data[type_dict['y_axis']],
                                           self.ax[plot_type][key],
                                           N_plot=N_plot
                                           )
                        self.ax[plot_type][key].set_xlabel(value_name)
                        self.ax[plot_type][key].set_ylabel(type_dict['y_axis'])
                        self.ax[plot_type][key].set_zlabel('{} Distribution'.format(value_name))
                        self.ax[plot_type][key].set_title(key)
                        self._myprint.decrease_indent()
            self._myprint.decrease_indent()

        elif(plot_type in ['correlation', '3d']):
            self._myprint('[3d plot]')
            del self._plot_type[plot_type][:]
            self._myprint.add_indent()
            self._set_fig_ax(type_dict,plot_type,plot_value=plot_value,directory=directory,label=label)

            for key in type_dict['2d_plot']:
                for value_name in type_dict['values']:
                    if(value_name in key):
                        self._myprint('[plot : {}]'.format(key))
                        self._plot_type[plot_type].append(key)
                        self._plot_2d_overlaid(
                                               data[type_dict['x_axis']],
                                               data[value_name],
                                               data[type_dict['y_axis']],
                                               self.ax[plot_type][key],
                                               label=type_dict['y_axis'],
                                               N_plot=N_plot
                                               )
                        self.ax[plot_type][key].set_xlabel(type_dict['x_axis'])
                        self.ax[plot_type][key].set_title(key)
                        self.ax[plot_type][key].set_ylabel('{}'.format(value_name))

            for key in type_dict['3d_plot']:
                for value_name in type_dict['values']:
                    if(value_name in key):
                        self._myprint('[plot : {}]'.format(key))
                        self._plot_type[plot_type].append(key)
                        self._plot_3d(
                                      self.ax[plot_type][key],
                                      data[type_dict['x_axis']],
                                      data[value_name],
                                      data[type_dict['y_axis']],
                                      N_plot=N_plot
                                      )
                        self.ax[plot_type][key].set_xlabel(type_dict['x_axis'])
                        self.ax[plot_type][key].set_ylabel(type_dict['y_axis'])
                        self.ax[plot_type][key].set_title(key)
                        self.ax[plot_type][key].set_zlabel('{}'.format(value_name))
            self._myprint.decrease_indent()

        elif(plot_type == 'totally'):
            self._myprint('[plot_type detect : totally]')
            del self._plot_type['totally'][:]
            self._set_fig_ax(type_dict,plot_type,plot_value=plot_value,directory=directory,label=label)
            value_name = 'Totally_plot'
            self._plot_type[plot_type].append(value_name)
            for counter, key in enumerate(type_dict['y_list']):
                self.ax[plot_type][value_name].xaxis.set_tick_params(labelsize=self.basic_size['font']*1.5)
                self.ax[plot_type][value_name].yaxis.set_tick_params(labelsize=self.basic_size['font']*1.5)
                value_axis = key
                label_t = key
                self._myprint('[plot : {}]'.format(key))
                self._myprint.add_indent()
                if(len(type_dict['y_list']) < 2):
                    self._plot_2d(
                                  self.ax[plot_type][value_name],
                                  data[type_dict['x_axis']],
                                  data[value_axis],
                                  label=label_t,
                                  log_scale=log_scale
                                  )
                else:
                    self._plot_2d(
                                  self.ax[plot_type][value_name],
                                  data[type_dict['x_axis']],
                                  data[value_axis],
                                  label=label_t,
                                  color=cm.rainbow(float(counter)/len(type_dict['y_list'])),
                                  log_scale=log_scale
                                  )
                self.ax[plot_type][value_name].set_xlabel(type_dict['x_axis'],fontsize=self.basic_size['font']*1.5)
                self.ax[plot_type][value_name].grid(which='both',color='black',linestyle='--')
                if('_' in os.path.basename(file_path)):
                    self._myprint('[file name has "_" : y-axis named by it]') 
                    file_name = os.path.basename(file_path)
                    self.ax[plot_type][value_name].set_ylabel(file_name.split('_')[-1].split('.')[0],fontsize=self.basic_size['font']*1.5)
                else:
                    self.ax[plot_type][value_name].set_ylabel(value_name,fontsize=self.basic_size['font']*1.5)
                self.ax[plot_type][value_name].legend(bbox_to_anchor=(1.1, 1),loc="upper right",fontsize=self.basic_size['font'])
                self._myprint.decrease_indent()

        elif(plot_type == 'normal'):
            self._myprint('[normal plot]')
            del self._plot_type[plot_type][:]
            self._myprint.add_indent()
            self._set_fig_ax(type_dict,plot_type,plot_value=plot_value,directory=directory,label=label)

            for key in type_dict['ACF_list']:
                value_axis = key
                value_axis_error = 'error_' + key
                value_name = key
                self._myprint('[plot : {}]'.format(value_name))
                self._myprint.add_indent()
                self._plot_type[plot_type].append(value_name)
                self._acf_plot_2d(
                                  self.ax[plot_type][value_name],
                                  data[type_dict['x_axis']],
                                  data[value_axis],
                                  y_error=data[value_axis_error]
                                  )
                self.ax[plot_type][value_name].set_xlabel(type_dict['x_axis'])
                self.ax[plot_type][value_name].set_ylabel(value_name)
                self._myprint.decrease_indent()

            for key in type_dict['With_error_list']:
                value_axis = key
                value_axis_error = 'error_' + key
                value_name = key
                self._myprint('[plot : {}]'.format(value_name))
                self._myprint.add_indent()
                self._plot_type[plot_type].append(value_name)
                self._plot_2d(
                              self.ax[plot_type][value_name],
                              data[type_dict['x_axis']],
                              data[value_axis],
                              y_error=data[value_axis_error],
                              label=self._label
                              )
                if(self._label):
                    self.ax[plot_type][value_name].legend(loc="upper right",fontsize=self.basic_size['font'])
                self.ax[plot_type][value_name].set_xlabel(type_dict['x_axis'])
                self.ax[plot_type][value_name].set_ylabel(value_name)
                self._myprint.decrease_indent()

            for key in type_dict['Rest_list']:
                value_axis = key
                value_name = key
                self._myprint('[plot : {}]'.format(value_name))
                self._myprint.add_indent()
                self._plot_type[plot_type].append(value_name)
                self._plot_2d(
                              self.ax[plot_type][value_name],
                              data[type_dict['x_axis']],
                              data[value_axis],
                              label=self._label
                              )
                if(self._label):
                    self.ax[plot_type][value_name].legend(loc="upper right",fontsize=self.basic_size['font'])
                self.ax[plot_type][value_name].set_xlabel(type_dict['x_axis'])
                self.ax[plot_type][value_name].set_ylabel(value_name)
                self._myprint.decrease_indent()

            value_name = 'Energy_totaly_plot'
            for key in type_dict['Energy_list']:
                value_axis = key
                value_axis_error = 'error_' + key
                if(len(self._label) > 0):
                    label_t = key + ' ' + self._label
                else:
                    label_t = key
                self._myprint('[plot : {}]'.format(value_name))
                self._myprint.add_indent()
                self._plot_type[plot_type].append(value_name)
                self._plot_2d(
                              self.ax[plot_type][value_name],
                              data[type_dict['x_axis']],
                              data[value_axis],
                              y_error=data[value_axis_error],
                              label=label_t
                              )
                self.ax[plot_type][value_name].set_xlabel(type_dict['x_axis'])
                self.ax[plot_type][value_name].set_ylabel(value_name)
                self.ax[plot_type][value_name].legend(loc="upper right",fontsize=self.basic_size['font'])
                self._myprint.decrease_indent()

            for key in self._plot_type[plot_type]:
                for key_t in type_dict['Exact_list']:
                    if(('exact_' + key) ==  key_t):
                        value_name = key
                        value_axis = key_t
                        self._myprint('[plot : {}]'.format(key_t))
                        self._myprint.add_indent()
                        self._plot_2d(
                                     self.ax[plot_type][value_name],
                                     data[type_dict['x_axis']],
                                     data[value_axis],
                                     label=key_t
                                     )
                        self._myprint.decrease_indent()
                        self.ax[plot_type][value_name].legend(loc="upper right",fontsize=self.basic_size['font'])

            for key in self.ax[plot_type].keys():
                self.ax['normal'][key].grid(which='both',color='black',linestyle='--')
            self._myprint.decrease_indent()

        self._myprint('[complete plot : {}]'.format(plot_type))
        if(plot_value != None):
            self.fig[plot_type].suptitle('{} '.format(plot_value), fontsize=self.basic_size['font'])
        else:
            self.fig[plot_type].suptitle('File : {} '.format(file_path), fontsize=self.basic_size['font'])

    def _genuine_hist_plot(self,data_range,data_hist,ax,label=None):
        self._myprint('[geniine hist plot]')
        total_number = np.sum(data_hist)
        n_bin = len(data_range)
        v_max = data_range.max()
        v_min = data_range.min()
        dv = data_range[1] - data_range[0]
        self._myprint('[dv : {}]'.format(dv))
        y_value = np.zeros(n_bin)
        normalizer = 0
        for i in range(n_bin):
            normalizer += dv * data_hist[i]
        self._myprint('[normalizer : {}]'.format(normalizer))
        y_value = data_hist / normalizer 
        if(label == None):
            label = 'unmodify'
        ax.bar(data_range , y_value , width=dv, label=label, alpha=0.4,color='blue')

    def _process_hist_plot(self,data_range,data_hist,ax,n_bin=0,label=None):
        self._myprint("[modified hist plot]")
        if(n_bin == 0):
            self._myprint('[not input n_bin, automatically set]')
            if(n_bin > 10000):
                n_bin = 100
                self._myprint('[detect n_bin is over 10000, set n_bin 100]')
            else:
                n_bin = len(data_range)
        self._myprint('[n_bin : {}]'.format(n_bin))
        total_number = np.sum(data_hist)
        total_number = int(total_number)
        hist,v_domain,dv= self._calc_hist(data_range,data_hist,n_bin)
        if(label == None):
            label = 'modify'
        ax.bar(v_domain , hist , width=dv, label=label, alpha=0.4)

    def _exact_gaussian_plot(self,data_range,data_hist,ax,T):
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
        self._myprint.add_indent()
        self._myprint("[mean : {0}, variance :  {1}, error : {2}]".format(mean, variance, error))
        self._myprint.decrease_indent()
        ax.plot(v,Gaussian,label='Gaussian:T={0:.3g}'.format(T))

    def _hist_plot_overlaid(self,data_range,data_hist,data_domain,ax,n_bin=0,N_plot=0,label=None):
        self._myprint('[modified hist plot 2d overlaid]')
        self._myprint.add_indent()
        if(N_plot ==0 or len(data_domain) < N_plot):
            N_plot = len(data_domain)
            loop_max = int(len(data_domain))
        else:
            loop_max = N_plot
        if(n_bin == 0):
            self._myprint('[not input n_bin, automatically set]')
            if(n_bin > 10000):
                n_bin = 100
                self._myprint('[detect n_bin is over 10000, set n_bin 100]')
            else:
                n_bin = len(data_range)
        self._myprint('[n_bin : {}]'.format(n_bin))
        self._myprint('[set loop_max : {}]'.format(loop_max))
        t_max = data_domain.max()
        for loop_t in range(loop_max):
            loop = loop_t * int(len(data_domain)/loop_max)
            hist,v_domain,dv= self._calc_hist(data_range[:,loop],data_hist[:,loop],n_bin)
            print_sentence = '[ d_range : {0:.4e}, numeric d_range : {1:.4e}]'.format( dv, data_range[1,0] - data_range[0,0])
            if(loop_max < 15):
                ax.bar(v_domain , hist , width=dv, color=cm.jet(data_domain[loop]/t_max), alpha=0.2, label='{0} : {1}'.format(label,data_domain[loop]))
            else:
                ax.bar(v_domain , hist , width=dv, color=cm.jet(data_domain[loop]/t_max), alpha=0.2)
            self._myprint.progress_bar(loop_t,loop_max,add_sentence=print_sentence)
        if(loop_max < 15):
            ax.legend(loc="upper right",prop = {'size':self.basic_size['font']})
        self._myprint.decrease_indent()

    def _hist_plot_3d(self,data_range,data_hist,data_domain,ax,n_bin=0,N_plot=0):
        self._myprint('[modified hist plot 3d]')
        self._myprint.add_indent()
        if(N_plot ==0 or len(data_domain) < N_plot):
            N_plot = len(data_domain)
            loop_max = int(len(data_domain))
        else:
            loop_max = N_plot
        if(n_bin == 0):
            self._myprint('[not input n_bin, automatically set]')
            if(n_bin > 10000):
                n_bin = 100
                self._myprint('[detect n_bin is over 10000, set n_bin 100]')
            else:
                n_bin = len(data_range)
        self._myprint('[set loop_max : {}]'.format(loop_max))
        t_max = data_domain.max()
        for loop_t in range(loop_max):
            loop = loop_t * int(len(data_domain)/loop_max)
            hist,v_domain,dv= self._calc_hist(data_range[:,loop],data_hist[:,loop],n_bin)
            print_sentence = '[ d_range : {0:.4e}, numeric d_range : {1:.4e}]'.format( dv, data_range[1,0] - data_range[0,0])
            ax.bar(v_domain , hist, data_domain[loop], zdir='y', width=dv, color=cm.jet(data_domain[loop]/t_max), alpha=0.5)
            self._myprint.progress_bar(loop_t,loop_max,add_sentence=print_sentence)
        self._myprint.decrease_indent()

    def _calc_hist(self,data_range,data_hist,n_bin):
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

    def _plot_3d(self,ax,data_range,data_z,data_domain,N_plot=0):
        self._myprint.add_indent()
        if(N_plot ==0 or len(data_domain) < N_plot):
            N_plot = len(data_domain)
            loop_max = int(len(data_domain))
        else:
            loop_max = N_plot
        x, y = np.meshgrid(data_range,data_domain,indexing='xy')
        for loop_t in range(loop_max):
            loop = loop_t * int(len(data_domain)/loop_max)
            ax.plot(x[loop,:],y[loop,:],data_z[:,loop],color=cm.jet(data_domain[loop]/data_domain.max()))
            self._myprint.progress_bar(loop_t,loop_max)
        self._myprint.decrease_indent()

    def _plot_2d_overlaid(self,data_range,data_z,data_domain,ax,N_plot=0,label=None):
        self._myprint.add_indent()
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
            self._myprint.progress_bar(loop_t,loop_max)
        if(loop_max < 15):
            ax.legend(loc="upper right",prop = {'size':self.basic_size['font']})
        self._myprint.decrease_indent()

    def _acf_plot_2d(self,ax,x,y,y_error=None,label=None):
        vv = y[0]
        y_t = y / vv
        if(isinstance(y_error,list)):
            ax.plot(x,y_t,label=label)
        else:
            if(isinstance(label,str)):
                ax.errorbar(x,y_t,yerr=y_error,label=label)
            else:
                ax.errorbar(x,y_t,yerr=y_error)

    def _plot_2d(self,ax,x,y,y_error=None,label=None,color=None,marker=None,log_scale=False):
        if(marker is None):
            marker = ''
        if(y_error is None):
            if(isinstance(label,str)):
                ax.plot(x,y,label=label,color=color,marker=marker)
            else:
                ax.plot(x,y,color=color,marker=marker)
        else:
            marker = 'x'
            if(isinstance(label,str)):
                ax.errorbar(x,y,yerr=y_error,label=label,color=color,marker=marker)
            else:
                ax.errorbar(x,y,yerr=y_error,color=color,marker=marker)
        if(log_scale):
            ax.set_yscale('log')  
            ax.set_xscale('log')  


def set_data_map(top_directory):
    config_data_map = []
    result_data_map = []

    top_depth = len([x for x in top_directory.split('/') if(len(x) > 0)])

    for current_directory, included_directory, files in os.walk(top_directory):
        current_dir_list = current_directory.split('/') 
        indent = len(current_dir_list)

        if('experiment_' in os.path.basename(current_directory)):
            json_path = os.path.join(current_directory,'parameter.json')
            if(os.path.exists(json_path)):
                json_data = json.load(open(json_path,'r'))
                config_data_map.append({})
                config_data_map[-1]['common_directory'] = os.path.dirname(current_directory)
                config_data_map[-1]['variable_parameters'] = []
                config_data_map[-1]['common_parameters'] = {'command_name':json_data['experiment_params']['command_name']}
                print_temp = lambda sentence : sentence
                simulate_params, total_combinations = set_total_combinations(json_data['simulate_params'],print_temp)
                for key, value in simulate_params.items():
                    if(not 'dir' in key and not 'time_info' in key):
                        if(isinstance(value, list) or isinstance(value,str)):
                            config_data_map[-1]['variable_parameters'].append(key)
                        else:
                            config_data_map[-1]['common_parameters'][key] = value

        if(not included_directory or 'number' in os.path.basename(current_directory)):
            result_files = []
            json_data = None
            for key in files:
                if('parameter.json' in key):
                    json_data = json.load(open(os.path.join(current_directory,key),'r'))
                if('result' in key):
                    result_files.append(key)
            result_data_map.append({})
            result_data_map[-1]['files'] = files
            result_data_map[-1]['directory'] = current_directory
            if(json_data):
                result_data_map[-1]['parameters'] = json_data['simulate_params']
                result_data_map[-1]['time_info'] = json_data['time_info']
                if(config_data_map):
                    result_data_map[-1]['common_directory'] = config_data_map[-1]['common_directory']
                    result_data_map[-1]['common_parameter_number'] = len(config_data_map) - 1
                    if(config_data_map[-1]['variable_parameters']):
                        result_data_map[-1]['variable_parameters'] = {} 
                        for key in config_data_map[-1]['variable_parameters']:
                            result_data_map[-1]['variable_parameters'][key] = json_data['simulate_params'][key]


    return copy.deepcopy(config_data_map), copy.deepcopy(result_data_map) 

