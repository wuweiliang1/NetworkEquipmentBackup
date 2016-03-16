import pexpect
import logging
import BackupHandler
import ipaddress
import functools


def backup_handle(ip, user, password, protocol, nodetype, nodename):
    if protocol is not ('telnet' or 'ssh'):
        logging.ERROR('Unknown login protocol %s' % protocol)
        return -1
    if nodetype is 'dell_blade_switch':
        pass
    elif nodetype is 'cisco_wlc':
        pass
    elif nodetype is 'hillstone_UTM':
        pass
    elif nodetype is 'citrix_MPX':
        pass
    elif nodetype is 'AX2100':
        pass
    elif nodetype is ('a2424' or 'a2208'):
        pass
    elif nodetype is '3dns':
        pass
    elif nodetype is 'h3c_switch':
        pass
    elif nodetype is 'cisco_switch':
        pass
    else:
        logging.ERROR("Can't resolve type " + nodetype + ", node backup will be skipped")
        return -1
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        logging.ERROR("%s is not a valid IP address" % ip)
        return -1


def dell_blade_switch_expect(ip, user, password, protocol, nodename):
    session = None
    try:
        if protocol is 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, password), timeout=10)
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
            session.sendline('enable\r')
            session.expect('#', timeout=5)
            session.sendline('write')
            session.expect('(y/n)', timeout=5)
            session.send('y')
            session.expect('Configuration Saved!', timeout=10)
            session.sendline('copy startup-config tftp://%s/%s/%s' % ())
            session.expect('(y/n)', timeout=5)
            session.send('y')
            session.expect('File transfer operation completed successfully', timeout=10)
    except pexpect.EOF:
        logging.ERROR('Abnormal End Of File Detected. The Script Logging is as follow')
    except pexpect.TIMEOUT:
        logging.ERROR('Operation Time out. Thread Exit. The Script Logging is as follow')
    finally:
        logging.INFO(session.read())
        session.close()


def cisco_wlc_expect(ip, user, password, protocol, nodename):
    session = None
    try:
        if protocol is 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, password), timeout=10)
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
        session.sendline('save config')
        session.expect('>', timeout=5)
        session.sendline('transfer upload datatype config')
        session.expect('>', timeout=5)
        session.sendline('transfer upload mode tftp')
        session.expect('>', timeout=5)
        session.sendline('transfer upload serverip %s' % ())
        session.expect('>', timeout=5)
        session.sendline('transfer upload filename /%s/%s' % ())
        session.expect('>', timeout=5)
        session.sendline('transfer upload start')
        session.expect('(y/n)', timeout=5)
        session.send('y')
        session.expect('File transfer operation completed successfully', timeout=10)
    except pexpect.EOF:
        logging.ERROR('Abnormal End Of File Detected. The Script Logging is as follow')
    except pexpect.TIMEOUT:
        logging.ERROR('Operation Time out. Thread Exit. The Script Logging is as follow')
    finally:
        logging.INFO(session.read())
        session.close()


def hillstone_utm_expect(ip, user, password, protocol, nodename):
    session = None
    try:
        if protocol is 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, password), timeout=10)
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
            session.sendline('enable\r')
            session.expect('#', timeout=5)
            session.sendline('write')
            session.expect('(y/n)', timeout=5)
            session.send('y')
            session.expect('Configuration Saved!', timeout=10)
            session.sendline('copy startup-config tftp://%s/%s/%s' % ())
            session.expect('(y/n)', timeout=5)
            session.send('y')
            session.expect('File transfer operation completed successfully', timeout=10)
    except pexpect.EOF:
        logging.ERROR('Abnormal End Of File Detected. The Script Logging is as follow')
    except pexpect.TIMEOUT:
        logging.ERROR('Operation Time out. Thread Exit. The Script Logging is as follow')
    finally:
        logging.INFO(session.read())
        session.close()

