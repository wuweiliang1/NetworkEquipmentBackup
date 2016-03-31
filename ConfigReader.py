import csv
import sys
import os
import logging
import configparser
import time
import argparse


class GlobalconfigReader:
    def __init__(self, location=sys.path[0] + '/Conf/backup.conf'):
        if os.path.exists(location) is True:
            logging.info('Find Backup.conf in %s' % location)
        config = configparser.ConfigParser()
        config.read(location)
        self._nodeconf = sys.path[0] + config['Global']['NodeConf']
        if os.path.exists(self._nodeconf) is not True:
            logging.critical('Could not find node configuration at %s' % self._nodeconf)
            exit(-1)
        self._scriptlocation = sys.path[0]
        self._backupaddr = config['Global']['BackupAddr']
        self._tftplocalmode = config['Global'].getboolean('tftplocalmode')
        self._localtftpfolder = config['Global']['localtftpfolder']
        self._mailmode = config['Global'].getboolean('mailmode')
        self._enforcemode = config['Global'].getboolean('enforcemode')
        argparser = argparse.ArgumentParser()
        argparser.add_argument("--enforce", help='Forcing all nodes initialize a backup routine',
                               action="store_true")
        argparser.add_argument("--mail", help='After finishing backup procedure, '
                                              'send a mail to predefined destination'
                               , action="store_true")
        self._cliargs = argparser.parse_args()
        if self._cliargs.enforce:
            self._enforcemode = True
        if self._cliargs.mail:
            self._mailmode = True

        if not self._tftplocalmode and self._mailmode:
            logging.error('You can not open mailmode while tftp local mode is off! Forcing mail mode to off.')
            self._mailmode = False
        if self._mailmode:
            try:
                self._mailsendto = config['Mail']['sendto']
                self._smtpserver = config['Mail']['SMTPServer']
                self._mailuser = config['Mail']['mailuser']
                self._mailuserpasswd = config['Mail']['mailpasswd']
            except KeyError:
                logging.error('Abnormal settings of mail configuration, Please check')
                exit(-1)

    @property
    def nodeconf(self):
        return self._nodeconf

    @property
    def backupaddr(self):
        return self._backupaddr

    @property
    def tftplocalmode(self):
        return self._tftplocalmode

    @property
    def localtftpfolder(self):
        return self._localtftpfolder

    @property
    def enforcemode(self):
        return self._enforcemode

    @property
    def mailmode(self):
        return self._mailmode

    @property
    def mailsendto(self):
        return self._mailsendto

    @property
    def smtpserver(self):
        return self._smtpserver

    @property
    def mailuser(self):
        return self._mailuser

    @property
    def mailuserpasswd(self):
        return self._mailuserpasswd

    @property
    def scriptlocation(self):
        return self._scriptlocation


class BackupNodeConfig:
    def __init__(self, nodecsv=sys.path[0] + '/Conf/node.csv', enforcemode=False):
        self._nodecsv = nodecsv
        self._nodelist = []
        self._classificationlist = []
        self._enforcemode = enforcemode
        with open(nodecsv, newline='') as ipcsv:
            self._nodereader = csv.DictReader(ipcsv, delimiter=',')
            for noderow in self._nodereader:
                # if noderow['protocol'] != 'telnet' and noderow['protocol'] != 'ssh':
                #     logging.error('Unknown login protocol %s of %s' % (noderow['protocol'], noderow['nodename']))
                #     continue
                # try:
                #     ipaddress.ip_address(noderow['nodeip'])
                # except ValueError:
                #     logging.error("%s %s is not a valid IP address" % (noderow['nodename'], noderow['nodeip']))
                #     continue
                self._nodelist.append(Node(noderow['nodename'], noderow['nodeip'], noderow['nodetype'],
                                           noderow['classification'], noderow['protocol'], noderow['backupstrategy'],
                                           noderow['lastbackuptime'], self._enforcemode))

    @property
    def nodelist(self):
        return self._nodelist

    @property
    def classificationlist(self):
        return self._classificationlist

    def updatetimestamp(self, result, backuptime_string):
        for node in self._nodelist:
            if result[node.nodename]:
                node.lastbackuptime = backuptime_string
        with open(self._nodecsv, newline='', mode='w') as ipcsv:
            nodewriter = csv.writer(ipcsv, delimiter=',')
            nodewriter.writerow(['nodename', 'nodeip', 'nodetype',
                                 'classification', 'protocol', 'backupstrategy', 'lastbackuptime'])
            for node in self._nodelist:
                nodewriter.writerow([node.nodename, node.nodeip, node.nodetype, node.classfication, node.protocol,
                                     node.backupstrategy, node.lastbackuptime])
        logging.info('Successfully updated the csv file')


class Node:
    """
    Node configuration class-object
    """

    def __init__(self, nodename, nodeip, nodetype, classfication, protocol, backupstrategy,
                 lastbackuptime, enforcemode):
        self._nodename = nodename
        self._nodeip = nodeip
        self._nodetype = nodetype
        self._classfication = classfication
        self._protocol = protocol
        self._backupstrategy = backupstrategy
        self._lastbackuptime = lastbackuptime
        self._enforcemode = enforcemode

    @property
    def nodename(self):
        return self._nodename

    @property
    def nodeip(self):
        return self._nodeip

    @property
    def nodetype(self):
        return self._nodetype

    @property
    def classfication(self):
        return self._classfication

    @property
    def protocol(self):
        return self._protocol

    @property
    def lastbackuptime(self):
        return self._lastbackuptime

    @lastbackuptime.setter
    def lastbackuptime(self, value):
        self._lastbackuptime = value

    @property
    def backupstrategy(self):
        return self._backupstrategy

    @property
    def needbackup(self):
        if self._enforcemode:
            return True
        day = int(time.strftime("%w"))
        if len(str(self._backupstrategy)) != 7:
            logging.error('Abnormal backup strategy of %s' % self._nodename)
            return False
        if int(str(self._backupstrategy)[day - 1]) > 0:
            backupperiod = 86400 / int(str(self._backupstrategy)[day - 1])
            if int(time.time()) > backupperiod + int(self._lastbackuptime):
                return True
            else:
                return False
