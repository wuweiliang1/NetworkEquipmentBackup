import ConfigReader
import time
import PexpectModule.pexpect
import logging
import Utils.Utils as Util
import sys


class BackupHandler:
    def __init__(self):
        self._backuptime_string = time.strftime("%Y%m%d%H%M", time.localtime())
        self._backuptime_timestamp = int(time.time())
        logging.basicConfig(level=logging.INFO,
                            filename='%s/log/%s-result.log' % (sys.path[0], self._backuptime_string))
        self._globalconfig = ConfigReader.GlobalconfigReader()
        self._backupnodeconfig = ConfigReader.BackupNodeConfig(nodecsv=self._globalconfig.nodeconf,
                                                               enforcemode=self._globalconfig.enforcemode)
        if self._globalconfig.tftplocalmode:
            classification = []
            for node in self._backupnodeconfig.nodelist:
                if node.needbackup and node.classfication not in classification:
                    classification.append(node.classfication)
            Util.create_classfication(self._globalconfig.localtftpfolder,
                                      self._backuptime_string, classification)
        self._nodelist = self._backupnodeconfig.nodelist
        self.result = None
        if self._nodelist is None:
            logging.critical('No backup node can be found!')
            exit(-1)

    @property
    def backuptime_string(self):
        return self._backuptime_string

    @property
    def backuptime_timestamp(self):
        return self._backuptime_timestamp

    def startbackup(self):
        self.result = PexpectModule.pexpect.backup_handle(self._nodelist, self._globalconfig.backupaddr,
                                                          self._backuptime_string, time.time())
        self._backupnodeconfig.updatetimestamp(self.result, self._backuptime_timestamp)

    def createtemp(self):
        Util.create_temp_folder(self._globalconfig.scriptlocation)

    def removetemp(self):
        if self._globalconfig.tftplocalmode:
            Util.remove_no_files_folder(self._globalconfig.localtftpfolder + '/' + self._backuptime_string)
        Util.remove_temp_folder(self._globalconfig.scriptlocation)

    def sendmail(self):
        if self._globalconfig.mailmode:
            Util.create_compressed_folder('%s%s' % (self._globalconfig.localtftpfolder, self._backuptime_string),
                                          '%s/temp' % sys.path[0], self._backuptime_string)
            mailsender = Util.Mail(self._globalconfig.mailsendto, self._globalconfig.smtpserver,
                                   self._globalconfig.mailuser, self._globalconfig.mailuserpasswd)
            plaincontent = ['Backing up all network devices configuration has been completed']
            for node in self.result:
                if not self.result[node]:
                    plaincontent.append('WARNING:Abnormal situations occur while handling %s' % node)
            plaincontent.append('For backup summary information, please check pexpect log and result log.')
            mailsender.send('--- 设备配置备份 --- %s ---' % self._backuptime_string,
                            plaincontent, '%s/temp/%s.tar.gz,%s/log/%s-pexpect.log,%s/log/%s-result.log'
                            % (sys.path[0], self._backuptime_string, sys.path[0], self._backuptime_string, sys.path[0],
                               self._backuptime_string))
        else:
            logging.info('Mail mode turn off. No mail is needed to be sent.')


if __name__ == '__main__':
    backuphandler = BackupHandler()
    backuphandler.createtemp()
    backuphandler.startbackup()
    backuphandler.sendmail()
    backuphandler.removetemp()
