# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-08-08 21:49:50
# @Last modified by:   LC
# @Last Modified time: 2017-03-23 17:01:54
# @Email: liangchaowu5@gmail.com

#########################################################################################
# Function: fetch user infomation, including address, phone, visa, names, and store them in redis
# 1. fetch american address from https://fakena.me/random-real-address/
# 2. fetch phone, visa from http://www.fakeaddressgenerator.com/World/us_address_generator
# 3. import user names from local file "names" into redis
#########################################################################################
 


import re
import time

import requests
from bs4 import BeautifulSoup 
from user_agent import generate_user_agent

from GetProxy import get_valid_proxy
from IgnoreWarnings import ignore_warnings
from ConnectRedis import get_connection



def get_address(proxy):
    """fetch american address from https://fakena.me/random-real-address/
    
    Args:
        proxy (str): proxy to visit the target site, ip:port
    
    Returns:
        format_addr (str): american address in the form of "address_line # city # state # zip"
    """
    ignore_warnings()
    url = r'https://fakena.me/random-real-address/'
    referer = r'https://fakena.me'
    header = {'user-agent' : generate_user_agent() , 'referer':referer }
    curr_proxy ={
    'http': 'http://%s'%proxy
    }

    text = requests.get(url, headers = header, proxies = curr_proxy).text
    pattern = re.compile('<strong>(.+)<br>(.+)</strong>')
    result = re.findall(pattern, text)
    if result: # sometimes the result is empty
        print result[0][0], result[0][1]
        address_line = result[0][0]
        city, state_zip = result[0][1].split(',')
        state, zip = state_zip.split()
        format_addr = address_line+'#'+city+'#'+state+'#'+zip
        return format_addr
    else:
        return ''


def get_phone_visa():
    """fetch phone, visa from http://www.fakeaddressgenerator.com/World/us_address_generator"""
    url = r'http://www.fakeaddressgenerator.com/World/us_address_generator'
    referer = r'http://www.fakeaddressgenerator.com/World'
    header = {'user-agent' : generate_user_agent() , 'referer':referer }
    text = requests.get(url, headers = header).text
    soup = BeautifulSoup(text, 'lxml')
    info = soup.find_all('input')
    """
    print 'name:',info[0]['value']
    print 'phone:',info[9]['value']
    print 'visa:',info[11]['value']
    print 'expires:',info[13]['value']
    """
    name_phone =  info[0]['value']+'#'+info[9]['value']
    name_visa = info[0]['value']+'#'+info[11]['value']+'#'+info[13]['value']
    print name_phone, name_visa
    return name_phone, name_visa


def get_user_names():
    r = get_connection(DB=1)
    with open('names') as f:
        for line in f:
            # print line.strip().title()
            r.sadd('user_name', line.strip().title())


if __name__ == '__main__':
    r = get_connection(DB = 3)
    crawl_address, crawl_phone_visa = True, False
    if crawl_address:
        count = 0
        while True:
            if count % 10 == 0:
                proxy = get_valid_proxy('https://fakena.me/random-real-address/', 'china_ips', referer = r'https://fakena.me')
                print 'current proxy: %s'%proxy
            addr = get_address(proxy) 
            if addr:   
                r.sadd('address', addr)
                print 'successfully add address %s to redis'%addr
            count += 1
            time.sleep(5)
    elif crawl_phone_visa:
        while True:
            name_phone, name_visa = get_phone_visa()
            r.sadd('name_phone', name_phone)
            r.sadd('name_visa', name_visa)
            print 'successfully add phone:%s, visa:%s to redis'%(name_phone, name_visa)
            time.sleep(5)
    else:
        print 'nothing to crawel'


