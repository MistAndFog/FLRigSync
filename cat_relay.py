#!/usr/bin/env python3

import sys
import time
import config
import utils.cat_client

from PySide6.QtCore import QObject, Signal

from sdr_control.hamlib import HamLibClient
from radio_control.dxlab import Commander
from radio_control.n1mm import N1MMClient
from radio_control.flrig import FlrigClient

from config import Config, DXLAB, N1MM, FLRIG, RUMLOG, NETWORK, LOCAL_HOST

MODE = "mode"
FREQUENCY = "frequency"
DESTINATION = "destination"
SOURCE = "source"
MESSAGE = 'message'
CHANGED = 'changed'

def sync_result(changed, source = None, destination = None, frequency = None, mode = None):
    result = {
        CHANGED: changed,
    }
    if changed:
        result.update({
            MESSAGE: f'Sync from {source} to {destination} {frequency}Hz {mode}',
            SOURCE: source,
            DESTINATION: destination,
            FREQUENCY: frequency,
            MODE: mode
        })
    return result


class CatRelay(QObject):
    # Signals
    connection_state_changed = Signal(bool)

    def __init__(self, params: config.Parameters):
        super().__init__()
        self.cat1_location = params.cat1_location
        self.cat1_software = params.cat1_software
        self.cat1_ip = params.cat1_ip
        self.cat1_port = params.cat1_port
        self.radio_info_port = params.radio_info_port
        self.cat2_software = params.cat2_software
        self.cat2_location = params.cat2_location
        self.cat2_ip = params.cat2_ip
        self.cat2_port = params.cat2_port

        self.cat1_client: utils.cat_client.CATClient = None
        self.cat2_client: utils.cat_client.CATClient = None

    def set_params(self, params: config.Parameters):
        self.cat1_location = params.cat1_location
        self.cat1_software = params.cat1_software
        self.cat1_ip = params.cat1_ip
        self.cat1_port = params.cat1_port
        self.radio_info_port = params.radio_info_port
        self.cat2_software = params.cat2_software
        self.cat2_location = params.cat2_location
        self.cat2_ip = params.cat2_ip
        self.cat2_port = params.cat2_port

    def is_connected(self):
        return self.cat1_client is not None and self.cat2_client is not None

    def connect_clients(self):
        try:
            self.cat1_client = self._connect_cat1()
            print(f'CAT1 software connected')

            self.cat2_client = self._connect_cat2()
            print(f'CAT2 software connected.')

        except Exception as e:
            print(e)
            self.disconnect_clients()

        finally:
            self.connection_state_changed.emit(self.is_connected())
            return self.is_connected()


    def disconnect_clients(self):
        # save current state
        old_state = self.is_connected()

        if self.cat1_client:
            self.cat1_client.close()
            self.cat1_client = None
            print(f'Cat Software disconnected')

        if self.cat2_client:
            self.cat2_client.close()
            self.cat2_client = None
            print(f'SDR disconnected.')

        new_state = self.is_connected()
        if old_state != new_state:
            self.connection_state_changed.emit(self.is_connected())

    def __del__(self):
        self.disconnect_clients()

    def _connect_sdr(self):
        ip_address = self.cat2_ip if self.cat2_location == NETWORK else LOCAL_HOST
        print(f'Connecting to {self.cat2_software} at {ip_address}:{self.cat2_port}')
        return HamLibClient(ip_address, self.cat2_port).__enter__()

    def _connect_cat1(self):
        ip_address = self.cat1_ip if self.cat1_location == NETWORK else LOCAL_HOST
        if self.cat1_software in [DXLAB, RUMLOG] :
            print(f'Connecting to {self.cat1_software} at {ip_address}:{self.cat1_port}')
            return  Commander(ip_address, self.cat1_port).__enter__()
        elif self.cat1_software == N1MM:
            print(f'Connecting to {self.cat1_software} at {ip_address}:{self.cat1_port}')
            return N1MMClient(self.radio_info_port, ip_address, self.cat1_port).__enter__()
        elif self.cat1_software == FLRIG:
            print(f'Connecting to {self.cat1_software} at {ip_address}:{self.cat1_port}')
            return FlrigClient(ip_address, self.cat1_port).__enter__()
        else:
            message = f'Cat software "{self.cat1_software}" is not supported!'
            print(message)
            raise Exception(message)

    def _connect_cat2(self):
        ip_address = self.cat2_ip if self.cat2_location == NETWORK else LOCAL_HOST
        if self.cat2_software in [DXLAB, RUMLOG] :
            print(f'Connecting to {self.cat2_software} at {ip_address}:{self.cat2_port}')
            return  Commander(ip_address, self.cat2_port).__enter__()
        elif self.cat2_software == N1MM:
            print(f'Connecting to {self.cat2_software} at {ip_address}:{self.cat2_port}')
            return N1MMClient(self.radio_info_port, ip_address, self.cat2_port).__enter__()
        elif self.cat2_software == FLRIG:
            print(f'Connecting to {self.cat2_software} at {ip_address}:{self.cat2_port}')
            return FlrigClient(ip_address, self.cat2_port).__enter__()
        else:
            message = f'Cat software "{self.cat2_software}" is not supported!'
            print(message)
            raise Exception(message)

    def sync(self):
        try:
            cat1_freq = self.cat1_client.get_freq()
            cat1_mode = self.cat1_client.get_mode()
            if (cat1_freq and cat1_freq != self.cat2_client.get_last_freq() and isinstance(cat1_freq, int)) or \
                    (cat1_mode and cat1_mode != self.cat2_client.get_last_mode() and isinstance(cat1_mode, str)):
                self.cat2_client.set_freq_mode(cat1_freq, cat1_mode)
                return sync_result(True, 'radio', 'SDR', cat1_freq, cat1_mode)
            else:
                cat2_freq = self.cat2_client.get_freq()
                cat2_mode = self.cat2_client.get_mode()
                if (cat2_freq and cat2_freq != self.cat1_client.get_last_freq() and isinstance(cat2_freq, int)) or \
                        (cat2_mode and cat2_mode != self.cat1_client.get_last_mode() and isinstance(cat2_mode, str)):
                    self.cat1_client.set_freq_mode(cat2_freq, cat2_mode)
                    return sync_result(True, 'SDR', 'radio', cat2_freq, cat2_mode)
            return sync_result(False)
        except Exception as e:
            print(e)
            self.connection_state_changed.emit(self.is_connected())
            return None


if __name__ == '__main__':
    # reconnect every RETRY_TIME seconds, until user press Ctrl+C
    params: config.Parameters = Config().params
    while True:
        try:
            cat_relay = CatRelay(params)
            cat_relay.connect_clients()
            while True:
                result = cat_relay.sync()
                if result:
                    if result[CHANGED]:
                        print(result[MESSAGE])
                else:
                    print('Sync failed')
                time.sleep(params.sync_interval)

        except KeyboardInterrupt as ke:
            print("\nTerminated by user.")
            cat_relay = None
            sys.exit()
        except Exception as e:
            retry_time = params.reconnect_time
            print(e)
            print(f'Retry in {retry_time} seconds ...')
            print('Press Ctrl+C to exit')
            time.sleep(retry_time)





