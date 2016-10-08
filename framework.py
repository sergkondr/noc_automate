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
        if len(self.number_of_jobs) > 63:
            self.number_of_threads = 63
        else:
            self.number_of_threads = len(self.number_of_jobs)
        
    def _worker(self, host):
        try:
            current_instance = self.command(host[1], host[0], self.login, self.password)
            result = current_instance.get_result()
            print(host[0] + " - ok")
            return result
        except Exception:
            return ['\n' + host[0], 'error']
            
    def start(self):
        with open(self.result_file, 'a') as result:
            pool = ThreadPool(self.number_of_threads)
            results = pool.map(self._worker, self.hosts)
            pool.close()
            pool.join()
            result.write('')
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
        self.header = 'site_id;serial number\n'

    def _get_result_of_command(self):
        self.telnet_instance.write(self.command)
        sleep(self.command_sleep)
        result = str(self.telnet_instance.read_very_eager().decode('utf-8').split()[13])
        self.telnet_instance.close()
        return [self.host_name, result + '\n']