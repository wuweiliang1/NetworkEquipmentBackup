import BackupNodeReader
import PexpectModule
import time


class BackupHandler:
    def __init__(self):
        self.globalconfig = BackupNodeReader.GlobalconfigReader()
        self.nodelist = BackupNodeReader.BackupNodeReader().getnodelist()
        if self.nodelist is None:
            raise Exception
        else:
            for node in self.nodelist:
                self.startsinglebackup(node)
        self._backuptime = time.strftime("%Y%m%d%H%M", time.localtime())

    def startsinglebackup(self, node):
        # 判断节点类型
        if node['type'] in self.globalconfig.typemapping:
            nodetype = self.globalconfig.typemapping[node['type']]

    @property
    def backuptime(self):
        return self._backuptime
