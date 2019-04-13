import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


class Email(object):
    def __init__(self):
        '''
        Constructor
        '''
        pass


class SendEmail(object):
    def __init__(self, username, pwd, senderAddr, receiveAddrs, subject, content):
        self.username = username
        self.password = pwd
        self.senderAddr = senderAddr
        self.receiveAddrs = receiveAddrs
        self.message = MIMEMultipart()
        self.message['From'] = self.FmtMailAddr(senderAddr)
        self.message['to'] = self.FmtMailAddr(receiveAddrs[0])
        self.message['subject'] = subject

        # ---这是文字部分---
        part = MIMEText(content)
        self.message.attach(part)

        # ---这是附件部分---
        # xlsx类型附件
        # part = MIMEApplication(open('foo.xls', 'rb').read())
        # part.add_header('Content-Disposition', 'attachment', filename="foo.xls")
        # self.message.attach(part)
        #
        # # jpg类型附件
        # part = MIMEApplication(open('foo.jpg', 'rb').read())
        # part.add_header('Content-Disposition', 'attachment', filename="foo.jpg")
        # self.message.attach(part)

        # # pdf类型附件
        # part = MIMEApplication(open('foo.pdf', 'rb').read())
        # part.add_header('Content-Disposition', 'attachment', filename="foo.pdf")
        # msg.attach(part)
        #
        # # mp3类型附件
        # part = MIMEApplication(open('foo.mp3', 'rb').read())
        # part.add_header('Content-Disposition', 'attachment', filename="foo.mp3")
        # msg.attach(part)

    def FmtMailAddr(self, mailAddr):  # 格式化 frommail及tomail
        return '<%s>' % mailAddr

    def Send(self):
        try:
            smtObj = smtplib.SMTP('smtp.163.com')
            smtObj.login(self.username, self.password)
            smtObj.sendmail(self.senderAddr, self.receiveAddrs, self.message.as_string())
            smtObj.quit()
            print("邮件发送成功")
        except smtplib.SMTPException as e:
            print(e)
            print("Error:无法发送邮件")