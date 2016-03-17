import csv
import sys
import os
import logging
import configparser


class GlobalconfigReader:
    def __init__(self, location=sys.path[0] + '/Conf/backup.conf'):
        if os.path.exists(location) is True:
            logging.INFO('Find Backup.conf in ' + location)
        config = configparser.ConfigParser()
        config.read(location)
        self._nodeconf = sys.path[0] + config['Global']['NodeConf']
        self._backupprotocol = config['Global']['BackupProtocol']
        self._backupaddr = config['Global']['BackupAddr']
        self._typemapping = {}
        for ModuleKey in config['Type Mapping']:
            self._typemapping[ModuleKey] = config['Type Mapping'][ModuleKey]

    @property
    def typemapping(self):
        return self._typemapping

    @property
    def nodeconf(self):
        return self._nodeconf

    @property
    def backupprotocol(self):
        return self._backupprotocol

    @property
    def backupaddr(self):
        return self._backupaddr


class BackupNodeReader:
    def __init__(self, nodecsv=sys.path[0] + '/Conf/iplist_internal.csv'):
        self._nodelist = None
        with open(nodecsv, newline='') as ipcsv:
            nodereader = csv.DictReader(ipcsv, delimiter=',')
            for noderow in nodereader:
                self._nodelist.append(noderow)

    def getnodelist(self):
        return self._nodelist


class Node:
    def __init__(self, nodename, nodeip, nodetype, classfication, protocol, backupperiod, lastbackuptime):
        self._nodename = nodename
        self._nodeip = nodeip
        self._nodetype = nodetype
        self._classfication = classfication
        self._protocol = protocol
        self._backupperiod = backupperiod
        self._lastbackuptime = lastbackuptime

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
    def backupperiod(self):
        return self._backupperiod

    @property
    def lastbackuptime(self):
        return self._lastbackuptime
