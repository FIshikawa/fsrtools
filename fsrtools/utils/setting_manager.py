import os
import json

class SettingManager:
    """
    Setting manager class, create directory , json file and so on

    Args:
        log_manager(LogManager) : Logger for announce the condtions.

    """

    def __init__(self,log_manager):
        self._log_manager = log_manager

    def set_directory(self,directory_name):
        if os.path.exists(directory_name) != True:
          os.mkdir(directory_name)
          self._log_manager('[Create : {}]'.format(directory_name))
        else:
          self._log_manager('[Already exist]')

    def json_set(self,parameter_dict,file_name):
        f = open(file_name,'w')
        json.dump(parameter_dict,f,indent=4)
        f.close()

