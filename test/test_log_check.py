import pytest
from fsrtools.simulation_tools import SimulationManager
from test_simulation_manager import set_data_for_test
from fsrtools.utils import log_check

def test_log_check(set_data_for_test):
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
    log_check('./test')

