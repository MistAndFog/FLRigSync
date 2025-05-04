import os
import yaml
from PySide6.QtCore import QObject, Signal
from pathlib import Path
import config

SDR_PP = 'SDR++'
VALID_SDRS = [SDR_PP]
CAT2_SOFTWARE = 'CAT2_SOFTWARE'
CAT2_LOCATION = 'CAT2_LOCATION'
CAT2_IP = 'CAT2_IP'
CAT2_PORT = 'CAT2_PORT'

CAT1_SOFTWARE = 'CAT1_Software'
CAT1_LOCATION = 'CAT_LOCATION'
CAT1_IP = 'CAT_IP'
CAT1_PORT = 'CAT_PORT'

RADIO_INFO_PORT = 'RADIO_INFO_PORT'

RECONNECT_TIME = 'RECONNECT_TIME'  # seconds
SYNC_INTERVAL = 'SYNC_TIME'  # seconds

PLACEHOLDER_SOFTWARE = '--select your software--'
DXLAB = 'DXLab'
RUMLOG = 'RUMLogNG'
N1MM = 'N1MM'
FLRIG = 'FLRIG'
VALID_CAT_SOFTWARES = [DXLAB, RUMLOG, N1MM, FLRIG]

CONFIG_FILE = 'cat-relay.yml'

LOCAL = 'This computer'
NETWORK = 'Another computer'
VALID_LOCATIONS = [LOCAL, NETWORK]

LOCAL_HOST = '127.0.0.1'

class Parameters(QObject):
    # Qt Signals
    CAT2_LOCATION_changed = Signal(str)
    cat_software_changed = Signal(str)
    cat_location_changed = Signal(str)

    def __init__(self,
                 cat1_software=FLRIG,
                 cat1_location=LOCAL,
                 cat1_ip=LOCAL_HOST,
                 cat1_port=4532,
                 cat2_location=LOCAL,
                 cat2_software=FLRIG,
                 cat2_ip=LOCAL_HOST,
                 cat2_port=5555,
                 radio_info_port=13063,
                 reconnect_time=10,
                 sync_interval=0.1
                 ):
        super().__init__(None)
        self.cat1_software = cat1_software
        self.cat1_location = cat1_location
        self.cat1_ip = cat1_ip
        self.cat1_port = cat1_port
        self.cat2_location = cat2_location
        self.cat2_software = cat2_software
        self.cat2_ip = cat2_ip
        self.cat2_port = cat2_port
        self.radio_info_port = radio_info_port
        self.reconnect_time = reconnect_time
        self.sync_interval = sync_interval

    def copy(self):
        return Parameters(
            self.cat1_software,
            self.cat1_location,
            self.cat1_ip,
            self.cat1_port,
            self.cat2_location,
            self.cat2_software,
            self.cat2_ip,
            self.cat2_port,
            self.radio_info_port,
            self.reconnect_time,
            self.sync_interval
        )

    def set_cat1_location(self, location):
        if self.cat1_location != location:
            self.cat1_location = location
            self.CAT2_LOCATION_changed.emit(location)

    def set_cat2_location(self, location):
        if self.cat2_location != location:
            self.cat2_location = location
            self.cat_location_changed.emit(location)

    def set_cat1_ip(self, ip):
        self.cat1_ip = ip

    def set_cat1_port(self, port):
        self.cat1_port = port

    def set_cat1_software(self, software):
        if self.cat2_software != software:
            self.cat2_software = software
            self.cat_software_changed.emit(software)

    def set_cat2_software(self, software):
        if self.cat2_software != software:
            self.cat2_software = software
            self.cat_software_changed.emit(software)

    def set_cat2_ip(self, ip):
        self.cat2_ip = ip

    def set_cat2_port(self, port):
        self.cat2_port = port

    def set_radio_info_port(self, port):
        self.radio_info_port = port

    def set_reconnect_time(self, seconds):
        self.reconnect_time = seconds

    def set_sync_interval(self, seconds):
        self.sync_interval = seconds


class Config:
    def __init__(self):
        self.params: config.Parameters = Parameters()

        script_dir = os.path.dirname(os.path.realpath(__file__))
        work_dir = os.getcwd()
        home_dir = Path.home()
        config_file_locations = [work_dir, home_dir, script_dir]
        self.config_file_full_path = None
        self.default_config_file_full_path = os.path.join(home_dir, CONFIG_FILE)
        for location in config_file_locations:
            config_file_full_path = os.path.join(location, CONFIG_FILE)
            if os.path.isfile(config_file_full_path):
                try:
                    print(f'Config file {config_file_full_path} found, reading configuration...')
                    with open(config_file_full_path) as c_file:
                        file_config = yaml.safe_load(c_file)
                        self.update_params_from(file_config)
                        self.config_file_full_path = config_file_full_path
                        break
                except Exception as e:
                    print(e)

    def update_params_from(self, params_dict):
        self.params.cat1_software = params_dict.get(CAT1_SOFTWARE, self.params.cat1_software)
        self.params.cat1_location = params_dict.get(CAT1_LOCATION, self.params.cat1_location)
        self.params.cat1_ip = params_dict.get(CAT1_IP, self.params.cat1_ip)
        self.params.cat1_port = params_dict.get(CAT1_PORT, self.params.cat1_port)
        self.params.cat2_software = params_dict.get(CAT2_SOFTWARE, self.params.cat2_software)
        self.params.cat2_location = params_dict.get(CAT2_LOCATION, self.params.cat2_location)
        self.params.cat2_ip = params_dict.get(CAT2_IP, self.params.cat2_ip)
        self.params.cat2_port = params_dict.get(CAT2_PORT, self.params.cat2_port)
        self.params.radio_info_port = params_dict.get(RADIO_INFO_PORT, self.params.radio_info_port)
        self.params.reconnect_time = params_dict.get(RECONNECT_TIME, self.params.reconnect_time)
        self.params.sync_interval = params_dict.get(SYNC_INTERVAL, self.params.sync_interval)

    def get_data(self):
        return {
            CAT1_SOFTWARE: self.params.cat1_software,
            CAT1_LOCATION: self.params.cat1_location,
            CAT1_IP: self.params.cat1_ip,
            CAT1_PORT: self.params.cat1_port,
            CAT2_LOCATION: self.params.cat2_location,
            CAT2_SOFTWARE: self.params.cat2_software,
            CAT2_IP: self.params.cat2_ip,
            CAT2_PORT: self.params.cat2_port,
            RADIO_INFO_PORT: self.params.radio_info_port,
            RECONNECT_TIME: self.params.reconnect_time,
            SYNC_INTERVAL: self.params.sync_interval
        }

    def save_to_file(self):
        config_file_path = None
        # Updating existing config file
        if self.config_file_full_path and os.path.isfile(self.config_file_full_path):
            config_file_path = self.config_file_full_path
            print(f'Updating config file at {config_file_path}')
        else: # create a new config file in HOME folder
            print(f'Creating new config file at {config_file_path}')
            config_file_path = self.default_config_file_full_path

        with open(config_file_path, 'w') as c_file:
            yaml_str = yaml.dump(self.get_data())
            c_file.write(yaml_str)

