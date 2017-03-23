# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-08-30 22:18:49
# @Last modified by:   LC
# @Last Modified time: 2017-03-23 20:32:48
# @Email: liangchaowu5@gmail.com

##############################################################
# monitoring the hosts excuting the task, run it in crontab
# you can also add other function like ping 
##############################################################
import subprocess
import smtplib
import string
import time
    
def ping(ip):
    """check if host is alive
    
    Args:
        ip (str): ip of the host 
    
    Returns:
        1 or 0: represent whether the host is up or not
    """
    command = 'ping -c 4 %s'%ip
    try:
        subprocess.check_call(command.split())
        print '======================host %s is up' %ip
        return 1
    except subprocess.CalledProcessError:
        print '======================host %s is down' %ip
        return 0



def send_email(subject, content):
    """send email when host is down, need to change your own email
    
    Args:
        subject (str): subject of the email
        content (str): content of the email
    
    Returns:
        None 
    """
    HOST="smtp.sina.com"
    PASSWORD="XXXXXXX"
    FROM="XXXX@sina.com"
    TO="XXXX@139.com"
    SUBJECT=subject
    
    body=string.join((
            "FROM: %s" %FROM,
            "TO: %s" %TO,
            "SUBJECT: %s" %SUBJECT,
            "",
            content),"\r\n")
    server=smtplib.SMTP()
    server.connect(HOST,'25')
    server.starttls()
    server.login(FROM,PASSWORD)
    server.sendmail(FROM,TO,body)
    server.quit()


if __name__ == '__main__':
    # hosts is a list of your machine, one for a line, represent as ip   
    with open('hosts') as f:
        lines = f.readlines()
        for line in lines:
            ip = line.strip()
            if ip:
                if ping(ip)==0:
                    time.sleep(10)
                    if ping(ip)==0:
                        send_email(subject = 'Ping Failure', content= 'Fail to ping %s'%ip)
                        print '=========send email successfully'
    