import pexpect
import logging
import BackupHandler
import ipaddress
import time
import sys

backuptime = time.strftime("%Y%m%d%H%M", time.localtime())
timestamp = time.time()
tftpaddr = "192.168.1.1"


def backup_handle(ip, user, password, protocol, nodetype, nodename, backupperiod='always', lastbackuptime=0):
    if protocol is not ('telnet' or 'ssh'):
        logging.ERROR('Unknown login protocol %s' % protocol)
        return -1
    if int(lastbackuptime) + int(backupperiod) > timestamp and backupperiod is not 'always':
        logging.INFO('%s do not satisfy backup period settings. Node will be omitted.' % nodename)
        return 0
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        logging.ERROR("%s %s is not a valid IP address" % (nodename, ip))
        return -1
    if nodetype is 'dell_blade_switch':
        expect_dell_blade_switch(ip, user, password, protocol, nodename)
    elif nodetype is 'cisco_wlc':
        expect_cisco_wlc(ip, user, password, protocol, nodename)
    elif nodetype is 'hillstone_UTM':
        expect_hillstone_utm(ip, user, password, protocol, nodename)
    elif nodetype is 'netscaler':
        expect_netscaler(ip, user, password, protocol, nodename)
    elif nodetype is 'a10':
        expect_a10(ip, user, password, protocol, nodename)
    elif nodetype is 'alteon':
        expect_a2424(ip, password, protocol, nodename)
    elif nodetype is '3dns':
        pass
    elif nodetype is 'h3c_switch':
        pass
    elif nodetype is 'cisco_switch':
        pass
    else:
        logging.ERROR("Can't resolve type " + nodetype + ", node backup will be skipped")
        return -1


def expect_dell_blade_switch(ip, user, password, protocol, nodename, enablepassword=''):
    session = None
    try:
        if protocol is 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=10)
            match = session.expect(['password:', '(yes/no)?'], timeout=10)
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes\n')
                session.expect('password:')
                session.sendline(password)
        elif protocol is 'telnet':
            session = pexpect.spawn('telnet %s' % ip)
            match = session.expect(['User:', '(y/n)?'], timeout=10)
            if match == 0:
                session.sendline(user)
            elif match == 1:
                session.sendline('y')
                session.expect('User:')
                session.sendline(user)
            session.expect('Password:')
            session.sendline(password)
        session.expect('>', timeout=5)
        session.sendline('enable')
        if enablepassword is not '':
            session.expect('word:', timeout=5)
            session.sendline(enablepassword)
        session.expect('#', timeout=5)
        session.sendline('write')
        session.expect('(y/n)', timeout=5)
        session.send('y')
        session.expect('Configuration Saved!', timeout=10)
        session.sendline('copy startup-config tftp://%s/%s/%s' % (tftpaddr, backuptime, nodename))
        session.expect('(y/n)', timeout=5)
        session.send('y')
        session.expect('File transfer operation completed successfully', timeout=100)
        logging.INFO('%s successfully finish backup' % nodename)
    except pexpect.EOF:
        logging.ERROR('Abnormal End Of File Detected. The Script Logging is as follow')
    except pexpect.TIMEOUT:
        logging.ERROR('Operation Time out. Thread Exit. The Script Logging is as follow')
    finally:
        logging.INFO(session.read())
        session.close()


def expect_cisco_wlc(ip, user, password, protocol, nodename):
    session = None
    try:
        if protocol is 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=10)
            match = session.expect(['User:', '(yes/no)?'], timeout=10)
            if match == 0:
                session.sendline(user)
            elif match == 1:
                session.sendline('yes')
                session.expect('User:')
                session.sendline(user)
            session.expect('Password:')
            session.sendline(password)
        elif protocol is 'telnet':
            logging.ERROR('Cisco WLC telnet login is not supported. The node will be skipped')
            return -1
        session.expect('>', timeout=5)
        session.sendline('save config')
        session.expect('(y/n)', timeout=5)
        session.send('y')
        session.expect('>', timeout=5)
        session.sendline('transfer upload datatype config')
        session.expect('>', timeout=5)
        session.sendline('transfer upload mode tftp')
        session.expect('>', timeout=5)
        session.sendline('transfer upload serverip %s' % tftpaddr)
        session.expect('>', timeout=5)
        session.sendline('transfer upload filename /%s/%s' % (backuptime, nodename))
        session.expect('>', timeout=5)
        session.sendline('transfer upload start')
        session.expect('(y/n)', timeout=5)
        session.send('y')
        session.expect('>', timeout=120)
        logging.INFO('%s successfully finish backup' % nodename)
    except pexpect.EOF:
        logging.ERROR('Abnormal End Of File Detected. The Script Logging is as follow')
    except pexpect.TIMEOUT:
        logging.ERROR('Operation Time out. Thread Exit. The Script Logging is as follow')
    finally:
        logging.INFO(session.read())
        session.close()


def expect_hillstone_utm(ip, user, password, protocol, nodename):
    session = None
    try:
        if protocol is 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=10)
            match = session.expect(['password:', '(yes/no)?'], timeout=10)
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes\n')
                session.expect('password:')
                session.sendline(password)
        elif protocol is 'telnet':
            logging.ERROR('hillstone utm telnet login is not supported. The node will be skipped')
            return -1
        session.expect('#', timeout=5)
        session.sendline('export configuration startup to tftp server %s %s/%s' % (tftpaddr, backuptime, nodename))
        session.expect('#', timeout=5)
        logging.INFO('%s successfully finish backup' % nodename)
    except pexpect.EOF:
        logging.ERROR('Abnormal End Of File Detected. The Script Logging is as follow')
    except pexpect.TIMEOUT:
        logging.ERROR('Operation Time out. Thread Exit. The Script Logging is as follow')
    finally:
        logging.INFO(session.read())
        session.close()


def expect_netscaler(ip, user, password, protocol, nodename):
    session = None
    try:
        if protocol is 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=10)
            match = session.expect(['password:', '(yes/no)?'], timeout=10)
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes\n')
                session.expect('password:')
                session.sendline(password)
        elif protocol is 'telnet':
            logging.ERROR('citrix mpx telnet login is not supported. The node will be skipped')
            return -1
        session.expect('>', timeout=5)
        session.sendline('save config')
        session.expect('>', timeout=5)
        session.sendline('shell')
        session.expect('#', timeout=5)
        session.sendline('tftp %s' % tftpaddr)
        session.expect('tftp>', timeout=5)
        session.sendline('put /nsconfig/ns.conf /%s/%s' % (backuptime, nodename))
        session.expect('>', timeout=10)
        logging.INFO('%s successfully finish backup' % nodename)
    except pexpect.EOF:
        logging.ERROR('Abnormal End Of File Detected. The Script Logging is as follow')
    except pexpect.TIMEOUT:
        logging.ERROR('Operation Time out. Thread Exit. The Script Logging is as follow')
    finally:
        logging.INFO(session.read())
        session.close()


def expect_a10(ip, user, password, protocol, nodename, enablepassword=''):
    session = None
    try:
        if protocol is 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=10)
            match = session.expect(['password:', '(yes/no)?'], timeout=10)
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes\n')
                session.expect('password:')
                session.sendline(password)
        elif protocol is 'telnet':
            logging.ERROR('a10 telnet login is not supported. The node will be skipped')
            return -1
        session.expect('>', timeout=5)
        session.sendline('enable')
        session.expect('Password:', timeout=5)
        session.sendline(enablepassword)
        session.expect('#', timeout=5)
        session.sendline('write memory')
        session.expect('#', timeout=5)
        session.sendline('configure')
        confmatch = session.expect(['(config)#', '(yes/no)'], timeout=10)
        if confmatch == 1:
            session.sendline('yes')
            session.expect('(config)#', timeout=10)
        session.sendline('copy running-config tftp://%s/%s/%s' % (tftpaddr, backuptime, nodename))
        session.expect('(config)#', timeout=20)
        logging.INFO('%s successfully finish backup' % nodename)
    except pexpect.EOF:
        logging.ERROR('Abnormal End Of File Detected. The Script Logging is as follow')
    except pexpect.TIMEOUT:
        logging.ERROR('Operation Time out. Thread Exit. The Script Logging is as follow')
    finally:
        logging.INFO(session.read())
        session.close()


def expect_a2424(ip, password, protocol, nodename):
    session = None
    try:
        if protocol is 'ssh':
            logging.ERROR('alteon ssh login is not supported. The node will be skipped')
            return -1
        elif protocol is 'telnet':
            session = pexpect.spawn('telnet %s' % ip)
            match = session.expect(['Enter password:', '(y/n)?'], timeout=10)
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('y')
                session.expect('Enter password:')
                session.sendline(password)
        session.expect('Main#', timeout=5)
        session.sendline('save')
        session.expect('Main#', timeout=5)
        session.sendline('/cfg/ptcfg')
        session.expect('Server:', timeout=5)
        session.sendline(tftpaddr)
        session.expect(':', timeout=5)
        session.sendline('/%s/%s' % (backuptime, nodename))
        session.expect(':', timeout=5)
        session.sendline()
        session.expect('Configuration#', timeout=5)
        logging.INFO('%s successfully finish backup' % nodename)
    except pexpect.EOF:
        logging.ERROR('Abnormal End Of File Detected. The Script Logging is as follow')
    except pexpect.TIMEOUT:
        logging.ERROR('Operation Time out. Thread Exit. The Script Logging is as follow')
    finally:
        logging.INFO(session.read())
        session.close()


def expect_3dns(ip, user, password, protocol, nodename):
    session = None
    try:
        if protocol is 'ssh':
            pexpect.spawn('scp %s@%s:/etc/named.conf %s/temp/%s.conf' % (user, ip, sys.path[0], nodename),
                          timeout=10)
            pexpect.spawn('scp -rp %s@%s:/config/3dns/namedb %s/temp/%s.db' % (user, ip, sys.path[0], nodename),
                          timeout=10)
            pexpect.spawn('scp %s@%s:/var/sysbackup/%s.ucs %s/temp/%s.ucs' %
                          (user, ip, time.strftime("%Y%m%d", time.localtime()), sys.path[0], nodename),
                          timeout=10)
            pexpect.spawn('/usr/bin/tftp %s' % tftpaddr, timeout=10)
        elif protocol is 'telnet':
            logging.ERROR('3dns telnet login is not supported. The node will be skipped')
            return -1
        session.expect('tftp>', timeout=5)
        session.sendline('put %s/temp/%s.conf %s/%s.conf' % (sys.path[0], nodename, backuptime, nodename))
        session.expect('tftp>', timeout=5)
        session.sendline('put %s/temp/%s.db %s/%s.db' % (sys.path[0], nodename, backuptime, nodename))
        session.expect('tftp>', timeout=5)
        session.sendline('put %s/temp/%s.ucs %s/%s.ucs' % (sys.path[0], nodename, backuptime, nodename))
        session.expect('tftp>', timeout=5)
        logging.INFO('%s successfully finish backup' % nodename)
    except pexpect.EOF:
        logging.ERROR('Abnormal End Of File Detected. The Script Logging is as follow')
    except pexpect.TIMEOUT:
        logging.ERROR('Operation Time out. Thread Exit. The Script Logging is as follow')
    finally:
        logging.INFO(session.read())
        session.close()


def expect_cisco_switch(ip, user, password, protocol, nodename):
    session = None
    try:
        if protocol is 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=10)
            match = session.expect(['password:', '(yes/no)?'], timeout=10)
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes\n')
                session.expect('password:')
                session.sendline(password)
        elif protocol is 'telnet':
            session = pexpect.spawn('telnet %s' % ip)
            match = session.expect(['name:', '(yes/no)?'], timeout=10)
            if match == 1:
                session.send('yes')
                session.expect('name:', timeout=10)
            session.sendline(user)
            session.expect('word:', timeout=10)
            session.sendline(password)
        session.expect('#', timeout=5)
        session.sendline('write memory')
        session.expect('#', timeout=10)
        session.sendline('copy startup-config tftp://%s/%s/%s' % (tftpaddr, backuptime, nodename))
        session.expect('Address', timeout=5)
        session.sendline()
        session.expect('Destination', timeout=5)
        session.sendline()
        session.expect('copied', timeout=15)
        logging.INFO('%s successfully finish backup' % nodename)
    except pexpect.EOF:
        logging.ERROR('Abnormal End Of File Detected. The Script Logging is as follow')
    except pexpect.TIMEOUT:
        logging.ERROR('Operation Time out. Thread Exit. The Script Logging is as follow')
    finally:
        logging.INFO(session.read())
        session.close()


def expect_h3c_switch(ip, user, password, protocol, nodename, src='M-GigabitEthernet 0/0/0'):
    session = None
    try:
        if protocol is 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=10)
            match = session.expect(['password:', '(yes/no)?'], timeout=10)
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes\n')
                session.expect('password:')
                session.sendline(password)
        elif protocol is 'telnet':
            logging.ERROR('alteon ssh login is not supported. The node will be skipped')
            return -1
        session.expect('>', timeout=5)
        session.sendline('save force')
        session.expect('>', timeout=10)
        session.sendline('tftp %s put flash://startup.cfg %s/%s.cfg source interface %s'
                         % (tftpaddr, backuptime, nodename, src))
        session.expect('>', timeout=15)
        logging.INFO('%s successfully finish backup' % nodename)
    except pexpect.EOF:
        logging.ERROR('Abnormal End Of File Detected. The Script Logging is as follow')
    except pexpect.TIMEOUT:
        logging.ERROR('Operation Time out. Thread Exit. The Script Logging is as follow')
    finally:
        logging.INFO(session.read())
        session.close()
