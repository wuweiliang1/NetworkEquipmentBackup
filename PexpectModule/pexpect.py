import pexpect
import logging
import time
import sys
import NodeAuthentication as Auth
import concurrent.futures
import io


def backup_handle(nodelist, _tftpaddr, _backuptime, _timestamp):
    """
    receive the nodelist and deliver every backup task to a single thread
    :param nodelist:Node class instance lists
    :param _tftpaddr: dst tftp address
    :param _backuptime: backuptime string
    :param _timestamp: timestamp string
    :return:
    """
    global tftpaddr, backuptime, timestamp, expectlog, result
    tftpaddr = _tftpaddr
    backuptime = _backuptime
    timestamp = _timestamp
    expectlog = open('%s/log/%s-pexpect.log' % (sys.path[0], backuptime), mode='w')
    result = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        for node in nodelist:
            if not node.needbackup:
                logging.info('%s do not satisfy backup strategy. Node will be omitted.' % node.nodename)
                result[node.nodename] = False
                continue
            else:
                executor.submit(backup_handle_single,
                                node.nodeip, Auth.NodeAuthentication(node.nodetype).user,
                                Auth.NodeAuthentication(node.nodetype).password,
                                node.protocol, node.nodetype, node.nodename,
                                node.classfication)
    expectlog.close()
    return result


def backup_handle_single(ip, user, password, protocol, nodetype, nodename, classfication='default'):
    """
    Matching nodetype to a specified pexpect handling function. If you want to add your own case for handling your node
    type, please add your case here.
    :param ip:
    :param user:
    :param password:
    :param protocol:
    :param nodetype:
    :param nodename:
    :param classfication:
    :return:
    """
    if nodetype == 'dell_blade_switch':
        expect_dell_blade_switch(ip, user, password, protocol, classfication, nodename)
    elif nodetype == 'cisco_wlc':
        expect_cisco_wlc(ip, user, password, protocol, classfication, nodename)
    elif nodetype == 'hillstone_UTM':
        expect_hillstone_utm(ip, user, password, protocol, classfication, nodename)
    elif nodetype == 'netscaler':
        expect_netscaler(ip, user, password, protocol, classfication, nodename)
    elif nodetype == 'ax':
        expect_a10_ax(ip, user, password, protocol, classfication, nodename)
    elif nodetype == 'thunder':
        expect_a10_thunder(ip, user, password, protocol, classfication, nodename)
    elif nodetype == 'alteon':
        expect_alteon(ip, password, protocol, classfication, nodename)
    elif nodetype == '3dns':
        expect_3dns(ip, user, password, protocol, classfication, nodename)
    elif nodetype == 'h3c_switch':
        expect_h3c_switch(ip, user, password, protocol, classfication, nodename)
    elif nodetype == 'ciscoSwitch':
        expect_cisco_switch(ip, user, password, protocol, classfication, nodename)
    else:
        logging.error("Can't resolve type " + nodetype + ", node backup will be skipped")
        result[nodename] = False


# def expect_template(ip, user, password, protocol, classfication, nodename, enablepassword=''):
#     """
#     expect template designing function. If you want to design your own processing pexpect routine, please follow this
#     template to code your own pexpect routine and get the best compatibility.
#     :param ip:The ip that you want to backup
#     :param user: username of managing your node
#     :param password: password of the username
#     :param protocol: the login protocol of your node. Should be one of ssh/telnet/scp.
#     :param classfication: the classfication string you specified in node.csv configuration file
#     :param nodename: nodename of your node
#     :param enablepassword: this parameter is not necessary if you do not need to enable on your deivce
#     """
#     flag = False  # Initialize the backup result flag as false
#     session = None
#     buffer = io.StringIO()  # Create a StringIO object for storing thread local buffer
#     buffer.writelines('\r==============%s@%s pexpect start==============\r' % (nodename, ip))
#     try:
#         if protocol == 'ssh':
#             # pexpect ssh logic
#             session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=60, encoding='utf-8', logfile=buffer)
#             # wait for asking password or confirmation
#             match = session.expect_exact(['password:', '(yes/no)?'])
#             if match == 0:  # If asking for password, send the password.
#                 session.sendline(password)
#             elif match == 1:  # If asking for confirmation , send yes. Then wait and send password
#                 session.sendline('yes')
#                 session.expect_exact('password:')
#                 session.sendline(password)
#         elif protocol == 'telnet':
#             # pexpect telnet logic
#             session = pexpect.spawn('telnet %s' % ip, encoding='utf-8', timeout=60, logfile=buffer)
#             match = session.expect_exact(['User:', '(y/n)?'])  # wait for asking username or confirmation
#             if match == 0:  # asking for username
#                 session.sendline(user)
#             elif match == 1:  # asking for confirmation
#                 session.sendline('y')
#                 session.expect_exact('User:')
#                 session.sendline(user)
#             session.expect_exact('Password:')
#             session.sendline(password)
#         session.expect_exact('>')  # wait for prompt
#         session.sendline('enable')  # enable for superuser privileges
#         if enablepassword != '':  # if enable password is not empty, wait for asking password and send it.
#             session.expect_exact('word:')
#             session.sendline(enablepassword)
#         session.expect_exact('#')  # superuser prompt
#         session.sendline('write')  # handle backup logic. First save the startup configuration file
#         session.expect_exact('(y/n)')
#         session.send('y')
#         session.expect_exact('Configuration Saved!')
#         # copy the startup-config to the specified tftp
#         session.sendline('copy startup-config tftp://%s/%s/%s/%s.cfg' % (tftpaddr, backuptime, classfication, nodename))
#         session.expect_exact('(y/n)')
#         session.send('y')
#         session.expect_exact('File transfer operation completed successfully', timeout=120)
#         logging.info('%s successfully finish backup' % nodename)
#         flag = True
#     except pexpect.EOF:  # EOF exception catch
#         logging.error('%s Abnormal End Of File Detected. Please check the pexpect log' % nodename)
#         flag = False
#     except pexpect.TIMEOUT:  # TIMEOUT exception catch
#         logging.error('%s Operation Time out. Thread Exit. Please check the pexpect log' % nodename)
#         flag = False
#     finally:
#         buffer.writelines('\r==============%s@%s pexpect end==============\r' % (nodename, ip))
#         expectlog.write(buffer.getvalue())  # write thread local buffer to global expectlog
#         buffer.close()
#         session.close()
#         result[nodename] = flag  # write the flag to global result list


def expect_dell_blade_switch(ip, user, password, protocol, classfication, nodename, enablepassword=''):
    flag = False
    session = None
    buffer = io.StringIO()
    buffer.writelines('\r==============%s@%s pexpect start==============\r' % (nodename, ip))
    try:
        if protocol == 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=60, encoding='utf-8', logfile=buffer)
            match = session.expect_exact(['password:', '(yes/no)?'])
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes')
                session.expect_exact('password:')
                session.sendline(password)
        elif protocol == 'telnet':
            session = pexpect.spawn('telnet %s' % ip, encoding='utf-8', timeout=60, logfile=buffer)
            match = session.expect_exact(['User:', '(y/n)?'])
            if match == 0:
                session.sendline(user)
            elif match == 1:
                session.sendline('y')
                session.expect_exact('User:')
                session.sendline(user)
            session.expect_exact('Password:')
            session.sendline(password)
        session.expect_exact('>')
        session.sendline('enable')
        if enablepassword != '':
            session.expect_exact('word:')
            session.sendline(enablepassword)
        session.expect_exact('#')
        session.sendline('write')
        session.expect_exact('(y/n)')
        session.send('y')
        session.expect_exact('Configuration Saved!')
        session.sendline('copy startup-config tftp://%s/%s/%s/%s.cfg' % (tftpaddr, backuptime, classfication, nodename))
        session.expect_exact('(y/n)')
        session.send('y')
        session.expect_exact('File transfer operation completed successfully', timeout=120)
        logging.info('%s successfully finish backup' % nodename)
        flag = True
    except pexpect.EOF:
        logging.error('%s Abnormal End Of File Detected. Please check the pexpect log' % nodename)
        flag = False
    except pexpect.TIMEOUT:
        logging.error('%s Operation Time out. Thread Exit. Please check the pexpect log' % nodename)
        flag = False
    finally:
        buffer.writelines('\r==============%s@%s pexpect end==============\r' % (nodename, ip))
        expectlog.write(buffer.getvalue())
        buffer.close()
        session.close()
        result[nodename] = flag


def expect_cisco_wlc(ip, user, password, protocol, classfication, nodename):
    flag = False
    session = None
    buffer = io.StringIO()
    buffer.writelines('\r==============%s@%s pexpect start==============\r' % (nodename, ip))
    try:
        if protocol == 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=60, encoding='utf-8', logfile=buffer)
            match = session.expect_exact(['User:', '(yes/no)?'])
            if match == 0:
                session.sendline(user)
            elif match == 1:
                session.sendline('yes')
                session.expect_exact('User:')
                session.sendline(user)
            session.expect_exact('Password:')
            session.sendline(password)
        elif protocol == 'telnet':
            logging.error('Cisco WLC telnet login is not supported. The node will be skipped')
            return -1
        session.expect_exact('>')
        session.sendline('save config')
        session.expect_exact('(y/n)')
        session.send('y')
        session.expect_exact('>')
        session.sendline('transfer upload datatype config')
        session.expect_exact('>')
        session.sendline('transfer upload mode tftp')
        session.expect_exact('>')
        session.sendline('transfer upload serverip %s' % tftpaddr)
        session.expect_exact('>')
        session.sendline('transfer upload filename /%s/%s/%s.cfg' % (backuptime, classfication, nodename))
        session.expect_exact('>')
        session.sendline('transfer upload start')
        session.expect_exact('(y/N)')
        session.send('y')
        session.expect_exact('>', timeout=200)
        logging.info('%s successfully finish backup' % nodename)
        flag = True
    except pexpect.EOF:
        logging.error('%s Abnormal End Of File Detected. Please check the pexpect log' % nodename)
        flag = False
    except pexpect.TIMEOUT:
        logging.error('%s Operation Time out. Thread Exit. Please check the pexpect log' % nodename)
        flag = False
    finally:
        buffer.writelines('\r==============%s@%s pexpect end==============\r' % (nodename, ip))
        expectlog.write(buffer.getvalue())
        buffer.close()
        session.close()
        result[nodename] = flag


def expect_hillstone_utm(ip, user, password, protocol, classfication, nodename):
    flag = False
    session = None
    buffer = io.StringIO()
    buffer.writelines('\r==============%s@%s pexpect start==============\r' % (nodename, ip))
    try:
        if protocol == 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=60, encoding='utf-8', logfile=buffer)
            match = session.expect_exact(['password:', '(yes/no)?'])
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes\n')
                session.expect_exact('password:')
                session.sendline(password)
        elif protocol == 'telnet':
            logging.error('hillstone utm telnet login is not supported. The node will be skipped')
            return -1
        session.expect_exact('#')
        session.sendline('export configuration startup to tftp server %s %s/%s/%s.cfg' % (tftpaddr, backuptime,
                                                                                          classfication, nodename))
        session.expect_exact('#')
        logging.info('%s successfully finish backup' % nodename)
        flag = True
    except pexpect.EOF:
        logging.error('%s Abnormal End Of File Detected. Please check the pexpect log' % nodename)
        flag = False
    except pexpect.TIMEOUT:
        logging.error('%s Operation Time out. Thread Exit. Please check the pexpect log' % nodename)
        flag = False
    finally:
        buffer.writelines('\r==============%s@%s pexpect end==============\r' % (nodename, ip))
        expectlog.write(buffer.getvalue())
        buffer.close()
        session.close()
        result[nodename] = flag


def expect_netscaler(ip, user, password, protocol, classfication, nodename):
    flag = False
    session = None
    buffer = io.StringIO()
    buffer.writelines('\r==============%s@%s pexpect start==============\r' % (nodename, ip))
    try:
        if protocol == 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=60, encoding='utf-8', logfile=buffer)
            match = session.expect_exact(['word:', '(yes/no)?'])
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes\n')
                session.expect_exact('word:')
                session.sendline(password)
            session.expect_exact('>')
            session.sendline('save config')
            session.expect_exact('>')
            session.sendline('shell')
            session.expect_exact('#')
            session.sendline('tftp %s' % tftpaddr)
            session.expect_exact('tftp>')
            session.sendline('put /nsconfig/ns.conf /%s/%s/%s.conf' % (backuptime, classfication, nodename))
            session.expect_exact('>')
            logging.info('%s successfully finish backup' % nodename)
            flag = True
        elif protocol == 'scp':
            session = pexpect.spawn('scp %s@%s:/nsconfig/ns.conf %s/temp/%s.conf' % (user, ip, sys.path[0], nodename),
                                    timeout=60, encoding='utf-8', logfile=buffer)
            session.expect_exact('word:')
            session.sendline(password)
            session.expect_exact('100%')
            session.close()
            tftpsession = pexpect.spawn('/usr/bin/tftp %s' % tftpaddr, timeout=60, encoding='utf-8', logfile=buffer)
            tftpsession.expect_exact('tftp>')
            tftpsession.sendline('put %s/temp/%s.conf %s/%s/%s.conf' % (sys.path[0], nodename, backuptime,
                                                                        classfication, nodename))
            tftpsession.expect_exact('tftp>')
            logging.info('%s successfully finish backup' % nodename)
            flag = True
        elif protocol == 'telnet':
            logging.error('citrix mpx telnet login is not supported. The node will be skipped')
            return -1

    except pexpect.EOF:
        logging.error('%s Abnormal End Of File Detected. Please check the pexpect log' % nodename)
        flag = False
    except pexpect.TIMEOUT:
        logging.error('%s Operation Time out. Thread Exit. Please check the pexpect log' % nodename)
        flag = False
    finally:
        buffer.writelines('\r==============%s@%s pexpect end==============\r' % (nodename, ip))
        expectlog.write(buffer.getvalue())
        buffer.close()
        session.close()
        result[nodename] = flag


def expect_a10_ax(ip, user, password, protocol, classfication, nodename, enablepassword=''):
    flag = False
    session = None
    buffer = io.StringIO()
    buffer.writelines('\r==============%s@%s pexpect start==============\r' % (nodename, ip))
    try:
        if protocol == 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=60, encoding='utf-8', logfile=buffer)
            match = session.expect_exact(['Password:', '(yes/no)?'])
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes\n')
                session.expect_exact('Password:')
                session.sendline(password)
        elif protocol == 'telnet':
            logging.error('a10 telnet login is not supported. The node will be skipped')
            return -1
        session.expect_exact('>')
        session.sendline('enable')
        session.expect_exact('Password:')
        session.sendline(enablepassword)
        session.expect_exact('#')
        session.sendline('write memory')
        session.expect_exact('#')
        session.sendline('configure')
        confmatch = session.expect_exact(['(config)#', '(yes/no)'])
        if confmatch == 1:
            session.sendline('yes')
            session.expect_exact('(config)#')
        session.sendline('backup config tftp://%s/%s/%s/%s.tar.gz' % (tftpaddr, backuptime, classfication, nodename))
        session.expect_exact('succeeded')
        logging.info('%s successfully finish backup' % nodename)
        flag = True
    except pexpect.EOF:
        logging.error('%s Abnormal End Of File Detected. Please check the pexpect log' % nodename)
        flag = False
    except pexpect.TIMEOUT:
        logging.error('%s Operation Time out. Thread Exit. Please check the pexpect log' % nodename)
        flag = False
    finally:
        buffer.writelines('\r==============%s@%s pexpect end==============\r' % (nodename, ip))
        expectlog.write(buffer.getvalue())
        buffer.close()
        session.close()
        result[nodename] = flag


def expect_a10_thunder(ip, user, password, protocol, classfication, nodename, enablepassword=''):
    flag = False
    session = None
    buffer = io.StringIO()
    buffer.writelines('\r==============%s@%s pexpect start==============\r' % (nodename, ip))
    try:
        if protocol == 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=60, encoding='utf-8', logfile=buffer)
            match = session.expect_exact(['Password:', '(yes/no)?'])
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes\n')
                session.expect_exact('Password:')
                session.sendline(password)
        elif protocol == 'telnet':
            logging.error('thunder telnet login is not supported. The node will be skipped')
            return -1
        session.expect_exact('>')
        session.sendline('enable')
        session.expect_exact('Password:')
        session.sendline(enablepassword)
        session.expect_exact('#')
        session.sendline('write memory')
        session.expect_exact('#')
        session.sendline('configure')
        confmatch = session.expect_exact(['(config)#', '(yes/no)'])
        if confmatch == 1:
            session.sendline('yes')
            session.expect_exact('(config)#')
        session.sendline('backup system use-mgmt-port tftp://%s/%s/%s/%s.tar.gz' %
                         (tftpaddr, backuptime, classfication, nodename))
        session.expect_exact('[yes/no]')
        session.sendline('no')
        session.expect_exact('succeeded')
        logging.info('%s successfully finish backup' % nodename)
        flag = True
    except pexpect.EOF:
        logging.error('%s Abnormal End Of File Detected. Please check the pexpect log' % nodename)
        flag = False
    except pexpect.TIMEOUT:
        logging.error('%s Operation Time out. Thread Exit. Please check the pexpect log' % nodename)
        flag = False
    finally:
        buffer.writelines('\r==============%s@%s pexpect end==============\r' % (nodename, ip))
        expectlog.write(buffer.getvalue())
        buffer.close()
        session.close()
        result[nodename] = flag


def expect_alteon(ip, password, protocol, classfication, nodename):
    flag = False
    session = None
    buffer = io.StringIO()
    buffer.writelines('\r==============%s@%s pexpect start==============\r' % (nodename, ip))
    try:
        if protocol == 'ssh':
            logging.error('alteon ssh login is not supported. The node will be skipped')
            return -1
        elif protocol == 'telnet':
            session = pexpect.spawn('telnet %s' % ip, timeout=60, encoding='utf-8', logfile=buffer)
            match = session.expect_exact(['word:', '(y/n)?'])
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('y')
                session.expect_exact('Enter password:')
                session.sendline(password)
        session.expect_exact('Main#')
        session.sendline('save')
        session.expect_exact('Main#')
        session.sendline('/cfg/ptcfg')
        session.expect_exact('server:')
        session.sendline(tftpaddr)
        session.expect_exact(':')
        session.sendline('/%s/%s/%s.cfg' % (backuptime, classfication, nodename))
        session.expect_exact(':')
        session.sendline()
        session.expect_exact('Configuration#')
        logging.info('%s successfully finish backup' % nodename)
        flag = True
    except pexpect.EOF:
        logging.error('%s Abnormal End Of File Detected. Please check the pexpect log' % nodename)
        flag = False
    except pexpect.TIMEOUT:
        logging.error('%s Operation Time out. Thread Exit. Please check the pexpect log' % nodename)
        flag = False
    finally:
        buffer.writelines('\r==============%s@%s pexpect end==============\r' % (nodename, ip))
        expectlog.write(buffer.getvalue())
        buffer.close()
        session.close()
        result[nodename] = flag


def expect_3dns(ip, user, password, protocol, classfication, nodename):
    flag = False
    tftpsession = None
    buffer = io.StringIO()
    buffer.writelines('\r==============%s@%s pexpect start==============\r' % (nodename, ip))
    try:
        if protocol == 'scp':
            session = pexpect.spawn('scp %s@%s:/etc/named.conf %s/temp/%s.conf' % (user, ip, sys.path[0], nodename),
                                    timeout=60, encoding='utf-8', logfile=buffer)
            session.expect_exact('password:')
            session.sendline(password)
            session.expect_exact('100%')
            session.close()
            session = pexpect.spawn('scp %s@%s:/var/sysbackup/%s.ucs %s/temp/%s.ucs' %
                                    (user, ip, time.strftime("%Y%m%d", time.localtime()), sys.path[0], nodename),
                                    timeout=60, encoding='utf-8', logfile=buffer)
            session.expect_exact('password:')
            session.sendline(password)
            session.expect_exact('100%')
            session.close()
        else:
            logging.error('3dns %s login is not supported. The node will be skipped' % protocol)
            return -1
        tftpsession = pexpect.spawn('/usr/bin/tftp %s' % tftpaddr, timeout=60, encoding='utf-8', logfile=buffer)
        tftpsession.expect_exact('tftp>')
        tftpsession.sendline('put %s/temp/%s.conf %s/%s/%s.conf' % (sys.path[0], nodename, backuptime,
                                                                    classfication, nodename))
        tftpsession.expect_exact('tftp>')
        tftpsession.sendline('put %s/temp/%s.ucs %s/%s/%s.ucs' % (sys.path[0], nodename, backuptime,
                                                                  classfication, nodename))
        tftpsession.expect_exact('tftp>')
        logging.info('%s successfully finish backup' % nodename)
        flag = True
    except pexpect.EOF:
        logging.error('%s Abnormal End Of File Detected. Please check the pexpect log' % nodename)
        flag = False
    except pexpect.TIMEOUT:
        logging.error('%s Operation Time out. Thread Exit. Please check the pexpect log' % nodename)
        flag = False
    finally:
        buffer.writelines('\r==============%s@%s pexpect end==============\r' % (nodename, ip))
        expectlog.write(buffer.getvalue())
        buffer.close()
        if tftpsession is not None:
            tftpsession.close()
        result[nodename] = flag


def expect_cisco_switch(ip, user, password, protocol, classfication, nodename):
    flag = False
    session = None
    buffer = io.StringIO()
    buffer.writelines('\r==============%s@%s pexpect start==============\r' % (nodename, ip))
    try:
        if protocol == 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=60, encoding='utf-8', logfile=buffer)
            match = session.expect_exact(['word:', '(yes/no)?'])
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes')
                session.expect_exact('word:')
                session.sendline(password)
        elif protocol == 'telnet':
            session = pexpect.spawn('telnet %s' % ip, encoding='utf-8', logfile=buffer, timeout=60)
            session.expect_exact("name: ")
            session.sendline(user)
            session.expect_exact('word: ')
            session.sendline(password)
        session.expect_exact('#')
        session.sendline('write memory')
        session.expect_exact('#')
        session.sendline('copy startup-config tftp://%s/%s/%s/%s.cfg' % (tftpaddr, backuptime, classfication, nodename))
        session.expect_exact('Address')
        session.sendline()
        session.expect_exact('Destination')
        session.sendline()
        session.expect_exact('copied')
        logging.info('%s successfully finish backup' % nodename)
        flag = True
    except pexpect.EOF:
        logging.error('%s Abnormal End Of File Detected. Please check the pexpect log' % nodename)
        flag = False
    except pexpect.TIMEOUT:
        logging.error('%s Operation Time out. Thread Exit. Please check the pexpect log' % nodename)
        flag = False
    finally:
        buffer.writelines('\r==============%s@%s pexpect end==============\r' % (nodename, ip))
        expectlog.write(buffer.getvalue())
        buffer.close()
        session.close()
        result[nodename] = flag


def expect_h3c_switch(ip, user, password, protocol, classfication, nodename, src='M-GigabitEthernet 0/0/0'):
    flag = False
    session = None
    buffer = io.StringIO()
    buffer.writelines('\r==============%s@%s pexpect start==============\r' % (nodename, ip))
    try:
        if protocol == 'ssh':
            session = pexpect.spawn('ssh %s@%s' % (user, ip), timeout=60, encoding='utf-8', logfile=buffer)
            match = session.expect_exact(['password:', '(yes/no)?'])
            if match == 0:
                session.sendline(password)
            elif match == 1:
                session.sendline('yes')
                session.expect_exact('password:')
                session.sendline(password)
        elif protocol == 'telnet':
            logging.error('alteon ssh login is not supported. The node will be skipped')
            return -1
        session.expect_exact('>')
        session.sendline('save force')
        session.expect_exact('>')
        session.sendline('tftp %s put flash:/startup.cfg %s/%s/%s.cfg source interface %s'
                         % (tftpaddr, backuptime, classfication, nodename, src))
        session.expect_exact('>')
        logging.info('%s successfully finish backup' % nodename)
        flag = True
    except pexpect.EOF:
        logging.error('%s Abnormal End Of File Detected. Please check the pexpect log' % nodename)
        flag = False
    except pexpect.TIMEOUT:
        logging.error('%s Operation Time out. Thread Exit. Please check the pexpect log' % nodename)
        flag = False
    finally:
        buffer.writelines('\r==============%s@%s pexpect end==============\r' % (nodename, ip))
        expectlog.write(buffer.getvalue())
        buffer.close()
        session.close()
        result[nodename] = flag
