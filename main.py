from time import strftime
from getpass import getpass

from framework import *

def main():
    i = int(input("""Menu:
    1. Get serial numbers from juniper
    2. Get software version from Juniper
    3. -                                    # Todo: compare configuration on NodeB/eNodeB and router
    >>> """))
    if i == 1:
        command = GetSerialNumbers
    elif i == 2:
        command = GetSoftwareVersion
    else:
        exit('[-] wrong choice')
    login = input('username: ').encode('utf-8') + '\r'.encode('utf-8')
    password = input('password: ').encode('utf-8') + '\r'.encode('utf-8')
    source_file = r'to_check.csv'
    result_file = source_file[:-3] + strftime('_%Y-%m-%d_%H-%M') + '.result.csv'
    
    work = MultithreadWorking(command, login, password, source_file, result_file)
    work.start()

if __name__ == '__main__':
    main()