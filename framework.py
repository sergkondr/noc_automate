from telnetlib import Telnet
from time import sleep


class TelnetPrototype():
    def __init__(self, host_IP, host_name, login, password, device_type='juniper'):
        self.host_IP = host_IP
        self.host_name = host_name
        self.login = login
        self.password = password
        self.device_type = device_type
        self.connection_timeout = 7
        self.command_sleep = 0.5
        self.header = ';'
        self.telnet_instance = self._connect()

    def _connect_to_juniper(self):
        try:
            telnet_instance = Telnet(self.host_IP, timeout=self.connection_timeout)
            sleep(self.command_sleep)
            telnet_instance.read_until(b'login: ')
            telnet_instance.write(self.login)
            telnet_instance.read_until(b'Password:')
            telnet_instance.write(self.password)
            telnet_instance.read_until(b'> ')
            return telnet_instance
        except:
            print('%s (%s)\t- not available' % (self.host_IP, self.host_name))
            print(NameError)
            raise NameError('connection error')

    def _connect_to_tellabs(self):
        try:
            telnet_instance = Telnet(self.host_IP, timeout=self.connection_timeout)
            sleep(self.command_sleep + 1)
            if telnet_instance.read_very_eager()[-1] != ord('>'):
                telnet_instance.write(self.login)
                telnet_instance.read_until(b'password:')
                telnet_instance.write(self.password)
                telnet_instance.read_until(b'>')
            else:
                telnet_instance.write(b' \r')
            return telnet_instance
        except:
            print('%s (%s)\t- not available' % (self.host_IP, self.host_name))
            raise NameError('connection error')

    def _connect(self):
        if self.device_type == 'juniper':
            return self._connect_to_juniper()
        elif self.device_type == 'tellabs':
            return self._connect_to_tellabs()
        else:
            return None

    def _get_result_of_command(self):
        pass

    def get_result(self):
        try:
            return self._get_result_of_command()
        except:
            self.telnet_instance.close()
            print('%s (%s)\t- command error' % (self.host_IP, self.host_name))
            raise NameError('command error')


class GetSerialNumbers(TelnetPrototype):
    def __init__(self, host_IP, host_name, login, password):
        TelnetPrototype.__init__(self, host_IP, host_name, login, password, 'juniper')
        self.command = b'show chassis hardware\n'
        self.header = 'site_id;serial number'

    def _get_result_of_command(self):
        self.telnet_instance.write(self.command)
        sleep(self.command_sleep)
        result = str(self.telnet_instance.read_very_eager().decode('utf-8').split()[13])
        self.telnet_instance.close()
        return ['\n' + self.host_name, result]
