import os
import stat
import logging
import tarfile
import email.mime.text
import email.mime.multipart
import smtplib
import shutil


def create_classfication(folder_location, folder_name, subfolder_list):
    """
    Create classfication folder in the local tftp folder(Avoid from not denying creating directory while uploading
    backup file)
    :param folder_location: Location you want to create root folder
    :param folder_name: Root folder name you want to create
    :param subfolder_list: list of subfolder name, should not be identical or contain special characters
    """
    try:
        os.mkdir(folder_location + folder_name)
        if os.name == 'posix':
            os.chmod(folder_location + folder_name, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        logging.info('Create and change permission of folder %s%s' % (folder_location, folder_name))
    except FileExistsError:
        logging.error('Error occurs on creating folder %s%s. Folder already exists.' % (folder_location, folder_name))
    for subfolder in subfolder_list:
        try:
            os.mkdir(folder_location + '/' + folder_name + '/' + subfolder)
            logging.info('Create and change permission of folder %s%s/%s' % (folder_location, folder_name, subfolder))
            if os.name == 'posix':
                os.chmod(folder_location + folder_name + '/' + subfolder, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        except FileExistsError:
            logging.error(
                'Error occurs on creating folder %s%s/%s. Folder already exists.' %
                (folder_location, folder_name, subfolder))
            continue


def create_compressed_folder(folder_location, dst_file_folder, filename):
    """
    Compress folder_location folder and storage into dst_file_folder/filename.tar.gz
    :param folder_location: Folder you want to compress into a tar file
    :param dst_file_folder: destination folder you want to put the compressed file
    :param filename: filename of compressed file you want to create
    """
    tar = tarfile.open('%s/%s.tar.gz' % (dst_file_folder, filename), 'w:gz')
    tar.add(folder_location)
    tar.close()


def create_temp_folder(folder_location):
    """
    Create a temp folder in the folder_location
    :param folder_location: Folder that you want to create the sub temp folder
    :return:
    """
    try:
        os.mkdir(folder_location+'/temp')
    except FileExistsError:
        logging.warning('Error occurs on creating folder %s/temp. Folder already exists.' % folder_location)


def remove_temp_folder(folder_location):
    """
    Remove a temp folder in the folder_location
    :param folder_location: Folder that you want to remove the sub temp folder
    :return:
    """
    shutil.rmtree(folder_location+'/temp')


class Mail:
    """
    Mail Class:
    Usage: mail = Mail("***@test.com.cn,***@test.com.cn","smtp_ipaddress(192.168.*.*)","mailloginuser","mailloginpasswd")
           mail.Send("sub","message","att1(/data/test.tar.gz),att2")
    Created by: KangTa
    Modified by: Wuweiliang
    """

    def __init__(self, adminuser, smtpserver, mailuser, mailpasswd):
        """
        初始化邮件实例所需全局参数
        """
        self._adminuser = adminuser.split(",")
        self._smtpserver = smtpserver
        self._mailuser = mailuser
        self._mailpasswd = mailpasswd

    def send(self, title, contentlist, filelist=''):
        """
        Mail邮件函数:主要用于发送邮件
        :param filelist: 要添加的附件文件列表
        :param contentlist: 邮件内容列表
        :param title: 邮件标题

        """
        # 邮件附件，创建邮件多内容对像
        msg = email.mime.multipart.MIMEMultipart()
        # 创建附件实例，打开指定附件，转码使用utf-8
        if filelist != "":
            filelist = filelist.split(",")
            for file in filelist:
                if os.path.exists(file):
                    filename = str(file).split("/")[-1]
                    attachment = email.mime.text.MIMEText(open(r'%s' % file, 'rb').read(), 'base64', 'utf-8')
                    attachment["Content-Type"] = 'application/octet-stream'
                    attachment["Content-Disposition"] = 'attachment; filename="%s"' % filename
                    # 邮件添加附件
                    msg.attach(attachment)
                else:
                    logging.error("Could not find %s." % file)
        content = None
        if len(contentlist) == 0:
            content = ''
        else:
            content = '\n'.join(contentlist)
        # 初始化邮件文本格式
        body = email.mime.text.MIMEText(content)
        # 邮件添加内容
        msg.attach(body)

        # 邮件基础信息填充
        msg['Subject'] = title
        msg['From'] = self._mailuser
        msg['To'] = ";".join(self._adminuser)

        # 邮件发送
        try:
            s = smtplib.SMTP()
            s.set_debuglevel(0)
            s.connect(self._smtpserver)
            s.login(self._mailuser, self._mailpasswd)
            s.sendmail(self._mailuser, self._adminuser, msg.as_string())
            s.close()
            return True
        except smtplib.SMTPAuthenticationError:
            return False
        except smtplib.SMTPConnectError:
            return False
