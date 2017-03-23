# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-07-04 21:04:49
# @Last modified by:   LC
# @Last Modified time: 2016-08-14 10:57:52
# @Email: liangchaowu5@gmail.com

##########################################################################
# Function: 
# 1. fetch proxies from site: http://www.xicidaili.com/,store them in redis
# 2. get a valid proxy for a certain site 
##########################################################################


import random
import time
import sys

import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent

from ConnectRedis import get_connection
from IgnoreWarnings import ignore_warnings


# proxies from different countries
CHINA = r'http://www.xicidaili.com/nn/' # china
OTHER = r'http://www.xicidaili.com/wn/' # other countries


def get_proxies(proxy_type, ip_set, start_page, end_page):
    """extract proxies from page source code, store them in redis
    
    Args:
        proxy_type (str): base url for proxy type, like the global variables CHINA and OTHER
        ip_set (str): which set should the ips be stored in redis
        start_page (int):  which page to start crawling
        end_page (int): which page to stop crawling
    """
    try:
        conn = get_connection()
    except Exception:
        print 'Error while connecting to redis'
        return
    proxies, curr_proxy =[], None
    for page in xrange(start_page, end_page+1):
        if page % 2 == 0:
            time.sleep(20)
        # get page source code
        headers = {'user-agent': generate_user_agent(), 'referer': 'http://www.xicidaili.com/'}
        text = requests.get(proxy_type+str(page), headers = headers).text
        # extract ips from source code
        soup = BeautifulSoup(text, 'lxml')
        for tr in soup.find_all('tr')[1:]:
            tds = tr.find_all('td')
            #if u'美国' in tds[3].text:
            proxy = tds[1].text+':'+tds[2].text               
            if is_valid('https://www.amazon.com/', proxy):
                conn.sadd(ip_set, proxy)
                print '%s added to ip set %s' %(proxy, ip_set)
            


def get_valid_proxy(target_url, ip_set, referer = 'https://www.google.com'):
    """extract a valid proxy for target_url from redis
    
    Args:
        target_url (str): url that need to visite with a proxy
        ip_set (str): the set in redis that stores proxies
        referer (str, optional): referer to construct headers for testing whether proxy is valid 
    
    Returns:
        curr_proxy(str): a valid proxy in the format of ip:port
    """
    try:
        conn = get_connection()
        proxies = conn.srandmember(ip_set, 5)
        curr_proxy  = proxies.pop()
        # if proxy is not valid, delete it from redis
        while not is_valid(target_url, curr_proxy, referer):
            conn.srem(ip_set, curr_proxy)
            if len(proxies) == 0:
                proxies = conn.srandmember(ip_set, 5)
            curr_proxy = proxies.pop()
        return curr_proxy
    except Exception, e:
        print 'Error while getting proxy from redis\n%s'%e.message
        sys.exit(0)



def is_valid(target_url, ip, referer):
    """judge if a proxy ip is valid for target_url
    
    Args:
        target_url (str): url that need to visite with a proxy
        ip (str): the set in redis to get 
        referer (str, optional): referer part of  headers  of the request
    
    Returns:
        boolean
    """
    ignore_warnings()
    proxy = {
    'http': 'http://%s' %ip
    }
    headers = {'user-agent': generate_user_agent(), 'referer': referer}
    try:
        r = requests.get(target_url, headers = headers, proxies = proxy, timeout = 6)
        return True
    except Exception:
        return False



if __name__ == '__main__':
    # disable the warnings from https website
    ignore_warnings()
    while True:
        get_proxies(CHINA, 'china_ips', 1,230)
        time.sleep(600)
    

