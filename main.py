from multiprocessing.dummy import Pool as ThreadPool
from time import strftime
from getpass import getpass

from framework import *


def get_hosts(source):
    try:
        hosts_file = open(source).readlines()
        hosts = []
        for s in hosts_file:
            s = s.split()
            hosts.append(s)
        return hosts
    except FileNotFoundError:
        print("No such file: %s" % source)
        return None
    except:
        print("Error: %s" % NameError)
        return None


def worker(host):
    try:
        current_instance = command(host[1], host[0], login, password)
        result = current_instance.get_result()
        print(host[0] + " - ok")
        return result
    except NameError:
        return ['\n' + host[0], NameError]


def main_thread(source_file, result_file):
    with open(result_file, 'a') as result:
        hosts = get_hosts(source_file)
        if hosts is None:
            raise NameError('Error opening source file')
        pool = ThreadPool(63 if len(hosts) > 63 else len(hosts))
        results = pool.map(worker, hosts)
        pool.close()
        pool.join()
        result.write('')
        for node in results:
            for parameter in node:
                print(parameter, end=';', file=result)
    print('finished')


def main():
    global login, password, command
    i = int(input("""Menu:
    1. Get serial numbers from juniper
    2. -
    >>> """))
    if i == 1:
        command = GetSerialNumbers
    else:
        print('err')
        return -1
    login = input('username: ').encode('utf-8') + '\r'.encode('utf-8')
    password = getpass('password: ').encode('utf-8') + '\r'.encode('utf-8')
    source_file = r'to_check.csv'
    result_file = source_file[:-3] + strftime('_%Y-%m-%d_%H-%M') + '.result.csv'
    main_thread(source_file, result_file)

if __name__ == '__main__':
    main()
