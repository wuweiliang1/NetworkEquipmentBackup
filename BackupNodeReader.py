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
    def __init__(self, nodecsv=sys.path[0] + '/Conf/iplist.csv'):
        self._nodelist = None
        with open(nodecsv, newline='') as ipcsv:
            nodereader = csv.DictReader(ipcsv, delimiter=',')
            for noderow in nodereader:
                self._nodelist.append(noderow)

    def getnodelist(self):
        return self._nodelist


class Node:
    def __init__(self, ip, hostname, loginmethod, updatecron, updateinterval):
        self._ip = ip
        self._hostname = hostname
        self._loginmethod = loginmethod
        self._updatecron = updatecron
        self._updateinterval = updateinterval

    @property
    def ip(self):
        return self._ip

    @property
    def hostname(self):
        return self._hostname

    @property
    def loginmethod(self):
        return self._loginmethod

    @property
    def updatecron(self):
        return self._updatecron

    @property
    def updateinterval(self):
        return self._updateinterval
