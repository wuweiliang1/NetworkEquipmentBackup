import BackupNodeReader
import time
import PexpectModule.pexpect


class BackupHandler:
    def __init__(self):
        self.globalconfig = BackupNodeReader.GlobalconfigReader()
        self._nodelist = BackupNodeReader.BackupNodeReader().getnodelist()
        self._backuptime = time.strftime("%Y%m%d%H%M", time.localtime())
        self._backupdate = time.strftime("%Y%m%d", time.localtime())
        if self._nodelist is None:
            raise Exception
        else:
            for node in self._nodelist:
                PexpectModule.pexpect.backup_handle()

    def _startsinglebackup(self, node):
        # 判断节点类型
        if node['type'] in self.globalconfig.typemapping:
            nodetype = self.globalconfig.typemapping[node['type']]

    @property
    def backuptime(self):
        return self._backuptime

if __name__ == '__main__':
    BackupHandler()
