from multiprocessing.dummy import Pool as ThreadPool
from telnetlib import Telnet
from time import sleep


class MultithreadWorking():
    def __init__(self, command, login, password, source_file, result_file):
        self.command = command
        self.login = login
        self.password = password

        self.source_file = source_file
        self.result_file = result_file

        self._get_jobs()
        self._get_number_of_jobs()
        self._get_number_of_threads()
        
    def _get_jobs(self):
        try:
            hosts_file = open(self.source_file).readlines()
            hosts = []
            for s in hosts_file:
                s = s.split()
                hosts.append(s)
            self.hosts = hosts
        except FileNotFoundError:
            exit("[-] No such file: \n%s" % self.source_file)
        except Exception:
            exit("[-] Something was wrong")
    
    def _get_number_of_jobs(self):
        self.number_of_jobs = len(self.hosts)
    
    def _get_number_of_threads(self):
        if self.number_of_jobs > 63:
            self.number_of_threads = 63
        else:
            self.number_of_threads = self.number_of_jobs
        
    def _worker(self, host):
        try:
            current_instance = self.command(host[1], host[0], self.login, self.password)
            self.header = current_instance.header
            result = current_instance.get_result()
            print(host[0] + " - ok")
        except Exception:
            result = ['\n' + host[0], 'error']
        return result
            
    def start(self):
        with open(self.result_file, 'a') as result:
            pool = ThreadPool(self.number_of_threads)
            results = pool.map(self._worker, self.hosts)
            pool.close()
            pool.join()
            result.write(self.header)
            for node in results:
                for parameter in node:
                    print(parameter, end=';', file=result)
        print('finished')


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
        self._connect()

    def _connect(self):
        try:
            self._get_telnet_connection()
            if self.device_type == 'juniper':
                self._auth_to_juniper()
            elif self.device_type == 'tellabs':
                self._auth_to_tellabs()
            print('%s - connected' %self.host_IP)
        except:
            print('%s (%s)\t- authorization failed' % (self.host_IP, self.host_name))

    def _get_telnet_connection(self):
        try:
            self.telnet_instance = Telnet(self.host_IP, timeout=self.connection_timeout)
        except:
            print('%s (%s)\t- not available' % (self.host_IP, self.host_name))
            self.telnet_instance = None
    
    def _auth_to_juniper(self):
        sleep(self.command_sleep)
        self.telnet_instance.read_until(b'ogin: ')
        self.telnet_instance.write(self.login)
        self.telnet_instance.read_until(b'assword:')
        self.telnet_instance.write(self.password)
        self.telnet_instance.read_until(b'> ')

    def _auth_to_tellabs(self):
       sleep(self.command_sleep + 1)
       if self.telnet_instance.read_very_eager()[-1] != ord('>'):
           self.telnet_instance.write(self.login)
           self.telnet_instance.read_until(b'assword:')
           self.telnet_instance.write(self.password)
           self.telnet_instance.read_until(b'>')
       else:
           self.telnet_instance.write(b' \r')

    def get_result(self):
        try:
            return self._get_result_of_command()
        except:
            self.telnet_instance.close()
            print('%s (%s)\t- command error' % (self.host_IP, self.host_name))
            raise NameError('command error')

    def _get_result_of_command(self):
        pass


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


class GetSoftwareVersion(TelnetPrototype):
    def __init__(self, host_IP, host_name, login, password):
        TelnetPrototype.__init__(self, host_IP, host_name, login, password, 'juniper')
        self.command = b'show version\n'
        self.header = 'site_id;model;version;'

    def _get_result_of_command(self):
        self.telnet_instance.write(self.command)
        sleep(self.command_sleep)
        result = str(self.telnet_instance.read_very_eager().decode('utf-8'))
        model = result[result.find('Model: ') + 7: result.find('\n', result.find('Model: '))].rstrip()
        junos_version = result[result.find('[') + 1: result.find(']')]
        self.telnet_instance.close()
        return ['\n' + self.host_IP, model, junos_version]


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
        self._connect()

    def _connect(self):
        try:
            self._get_telnet_connection()
            if self.device_type == 'juniper':
                self._auth_to_juniper()
            elif self.device_type == 'tellabs':
                self._auth_to_tellabs()
            print('%s - connected' %self.host_IP)
        except:
            print('%s (%s)\t- authorization failed' % (self.host_IP, self.host_name))

    def _get_telnet_connection(self):
        try:
            self.telnet_instance = Telnet(self.host_IP, timeout=self.connection_timeout)
        except:
            print('%s (%s)\t- not available' % (self.host_IP, self.host_name))
            self.telnet_instance = None
    
    def _auth_to_juniper(self):
        sleep(self.command_sleep)
        self.telnet_instance.read_until(b'ogin: ')
        self.telnet_instance.write(self.login)
        self.telnet_instance.read_until(b'assword:')
        self.telnet_instance.write(self.password)
        self.telnet_instance.read_until(b'> ')

    def _auth_to_tellabs(self):
       sleep(self.command_sleep + 1)
       if self.telnet_instance.read_very_eager()[-1] != ord('>'):
           self.telnet_instance.write(self.login)
           self.telnet_instance.read_until(b'assword:')
           self.telnet_instance.write(self.password)
           self.telnet_instance.read_until(b'>')
       else:
           self.telnet_instance.write(b' \r')

    def get_result(self):
        try:
            return self._get_result_of_command()
        except:
            self.telnet_instance.close()
            print('%s (%s)\t- command error' % (self.host_IP, self.host_name))
            raise NameError('command error')

    def _get_result_of_command(self):
        pass


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


class GetSoftwareVersion(TelnetPrototype):
    def __init__(self, host_IP, host_name, login, password):
        TelnetPrototype.__init__(self, host_IP, host_name, login, password, 'juniper')
        self.command = b'show version\n'
        self.header = 'site_id;model;version;'

    def _get_result_of_command(self):
        self.telnet_instance.write(self.command)
        sleep(self.command_sleep)
        result = str(self.telnet_instance.read_very_eager().decode('utf-8'))
        model = result[result.find('Model: ') + 7: result.find('\n', result.find('Model: '))].rstrip()
        junos_version = result[result.find('[') + 1: result.find(']')]
        self.telnet_instance.close()
        return ['\n' + self.host_IP, model, junos_version]
