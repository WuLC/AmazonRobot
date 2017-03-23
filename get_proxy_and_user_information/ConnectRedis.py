# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-07-10 16:50:47
# @Last modified by:   LC
# @Last Modified time: 2017-03-23 18:51:08
# @Email: liangchaowu5@gmail.com

###############################################################################################################
# Function: get a connection to redis
#
# details of dbs of redis:
# db0(proxy): china_ips, american_ips, amazon_ips, 
# db1(registered users, same password(SCutAmazon1234$), "mail#mac"): china_users, china_user_1, china_user_2
# db2(registered users, specific password, "mail#password#mac"): valid_users
# db3(user infomation for registering): user_name, address, name_phone, name_visa_expire
###############################################################################################################


import redis


def get_connection(HOST = 'XXXX', PORT = 6379, PASSWORD = 'XXXX', DB = 0):
    """get a connection to redis
    
    Args:
        HOST (str, optional): IP of redis server
        PORT (int, optional): the port that redis server listening
        PASSWORD (str, optional): password to the redis-server
        DB (int, optional): number of the db(0~15), default 0
    """
    r = redis.Redis(host = HOST, port = PORT, password = PASSWORD, db= DB)
    return r


if __name__ == '__main__':
    # manipulation on set
    ip_set = 'amazon_ips'
    r = get_connection()
    proxy = r.srandmember(ip_set, 5)
    r.srem(ip_set, proxy[0])
    print proxy
