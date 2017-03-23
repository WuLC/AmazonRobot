# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-08-15 22:34:08
# @Last modified by:   LC
# @Last Modified time: 2017-03-23 17:25:42
# @Email: liangchaowu5@gmail.com

###################################################################################
# Function: simulate some actions manipulated by humans with gui, including:
# 1. sign up and sign in
# 2. search keywords and visit target product
# 3. add product to cart
###################################################################################


import time
import random
import requests
import redis
import sys
import string

from user_agent import generate_user_agent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.proxy import *

# change mac address is useless
# from scripts.ChangeMacAddress import change_mac_address, generate_mac_address 
from get_proxy_and_user_information.ConnectRedis import get_connection
from get_proxy_and_user_information.IgnoreWarnings import ignore_warnings
from get_proxy_and_user_information.GetProxy import get_valid_proxy
from record_product_information.VisitRecord import update_record



class Robot:
    def __init__(self, proxy):
        """init the webdriver by setting the proxy and user-agent
        
        Args:
            proxy (str): proxy in the form of ip:port
        """
        # set proxy
        ip, port = proxy.split(':')
        profile = webdriver.FirefoxProfile()
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", ip)
        profile.set_preference("network.proxy.http_port", port)
        # set user_agent
        profile.set_preference("general.useragent.override", generate_user_agent())

        profile.update_preferences()
        self.driver = webdriver.Firefox(firefox_profile=profile)
        
        print 'current proxy: %s'%proxy


    def sign_up(self, sign_up_form, sign_up_url = r'https://www.amazon.com/ap/register?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_custrec_newcust'):
        """sign up with randomly generate user
        
        Args:
            sign_up_form (dict): some infomation required to sign up: name, e-mail and password
            sign_up_url (str, optional): url to sign up, custom url can jumps to the target url after signing up
        """
        # generate and change mac address 
        # mac = generate_mac_address()
        #change_mac_address(mac)
        try:
            self.driver.get(sign_up_url)
            for k,v in sign_up_form.items():
                inputElement = self.driver.find_element_by_name(k)
                inputElement.send_keys(v)
                time.sleep(5)
            inputElement.submit()
            user_info = sign_up_form['email']+'#'+sign_up_form['password']+'#'+mac
            self.store_registered_user(user_info)
        except Exception, e:
            print 'Error while signing up\n%s'%e.message
            self.exit_driver()
            sys.exit(0)
        

    def sign_in(self, sign_in_url = r'https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin'):
        """sign in with a registered user
        
        Args:
            sign_in_url (str, optional): url to sign in, custom url can jumps to the target url after signing in
        """
        sign_in_form = {}
        try:
            # randomly get a user from redis
            r = get_connection(DB = 1)
            info = r.srandmember('china_users',1)[0].split('#')
            if len(info) == 3:
                mail_box, passwd, mac = info
            elif len(info) == 2:
                mail_box, mac = info
                passwd = 'ScutAmazon1234$'
            #change_mac_address(mac)
            sign_in_form = {'email':mail_box, 'password':passwd}
            
            # sign_in
            self.driver.get(sign_in_url)
            for k,v in sign_in_form.items():
                inputElement = self.driver.find_element_by_name(k)
                inputElement.send_keys(v)
                time.sleep(5)
            inputElement.submit()
        except Exception, e:
            print 'Error while getting a user from redis and signing in\n%s'%e.message
            self.exit_driver()
            sys.exit(0)
                

    def simulate_browsing(self, words, asin , possibility, qid = None):
        """generate target url in terms of key words to search the item and the asin of the item,
           visit the url and add to cart within certain probability
        
        Args:
            words (str): words used to search items, seperated by space
            asin (str): ASIN of the item
            possibility (flaot): probability of adding item to cart
        """
        key_words = '+'.join(words.split())
        if qid:
            target_url = 'https://www.amazon.com/dp/%s/ie=UTF8&qid=%s&keywords=%s' %(asin, qid, key_words)
        else:
            target_url = 'https://www.amazon.com/dp/%s/ie=UTF8&keywords=%s' %(asin, key_words)
        #self.search_keywords(key_words)
        try:
            self.driver.get(target_url)
            update_record(asin, key_words, 'pv', number=1)
            time.sleep(10)
            """
            if random.random()< possibility:
                self.add_to_cart()
                time.sleep(5)
                update_record(asin, key_words, 'cart', number=1)
                print '========successfully add item to cart======'
            """
            # add to wish list
            wish_list = '#add-to-wishlist-button-submit'
            self.driver.find_element_by_css_selector(wish_list).click()
            time.sleep(15)
            # alert = self.driver.switch_to_alert() # NoAlertPresentException
            
        except ValueError, e:
            print 'Error while visiting %s\n%s'%(target_url, e.message)
            #self.exit_driver()
            sys.exit(0)


    def search_keywords(self, words):
        """type in keywords to search on the index page of amazon
        
        Args:
            words (str): words used to search items, seperated by space
        """
        try:
            self.driver.get(r'https://www.amazon.com/')
            inputElement = self.driver.find_element_by_name('field-keywords')
            inputElement.send_keys(words)
            inputElement.submit()
        except Exception, e:
            print 'Error while searching keywords\n%s'%e.message
            self.exit_driver()
            sys.exit(0)
            

    def add_to_cart(self):
        """add item to cart"""
        cart = '#add-to-cart-button'
        try:
            self.driver.find_element_by_css_selector(cart).click()
            print '================successfully add to cart==================='
            time.sleep(5)
        except Exception,e:
            print 'Error while adding item to cart\n%s'%e.message
            self.exit_driver()
            sys.exit(0)
        

    def generate_sign_up_user(self, random_password = False):
        """ramdomly generate a user to sign up
        
        Args:
            random_password (bool, optional): use uniform password or specific password
        """
        # user name
        conn = get_connection(DB=3)
        user_name = conn.srandmember('user_name', 1)[0]
        
        # mail box
        prefix  = string.digits+string.lowercase
        postfix = ['@126.com', '@163.com', '@sina.com', '@gmail.com', '@139.com', '@foxmail.com']
        prefix_len = random.randint(5,12)
        mail = ''
        for i in xrange(prefix_len):
            mail += random.choice(prefix)
        mail_box = mail+random.choice(postfix)

        # password
        if random_password:
            candidates = string.digits+string.letters+'!@$%&*+-_'
            passwd = ''
            for i in xrange(random.randint(7,17)):
                passwd += random.choice(candidates)
        else:
            passwd = 'ScutAmazon1234$'

        sign_up_form = {'customerName':user_name, 'email':mail_box, 'password':passwd, 'passwordCheck':passwd}
        return sign_up_form


    def store_registered_user(self, user_info):
        """store infomation of registered user in redis
        
        Args:
            user_info (str): infomation of registered user in the form of  mail#password#mac or mail#mac
        """
        try:
            if len(user_info.split('#')) == 3:
                DB = 2
                user_set = 'valid_users'
            elif len(user_info.split('#')) == 2:
                DB = 1
                user_set = 'china_users'
            else:
                print 'Error while storing user in redis, wrong format of user infomation\n %s'%info
                sys.exit(0)

            conn = get_connection(DB = DB)
            conn.sadd(user_set, user_info)
            print '===========successfully add user %s to reids:%s:%s==============' %(user_info, DB, user_set)
        except Exception, e:
            print 'Error while adding registered user to redis\n %s'%(e.message)
            sys.exit(0)


    def exit_driver(self):
        """exit the webdriver"""
        try:
            self.driver.quit()
        except Exception, e:
            print 'Error while exiting the web driver\n%s'%e.message


if __name__ == '__main__':
    asin = 'B002NSMFOQ'
    words = 'shower curtain rings'
    add_to_cart_probability = 0.7
    while True:
        proxy = get_valid_proxy('https://www.amazon.com', 'china_ips')
        robot = Robot(proxy)
        ###############################################
        # sign in and browse
        ###############################################
        robot.sign_in()
        # one item
        #robot.search_keywords(words)
        robot.simulate_browsing(words, asin, add_to_cart_probability)
        # another item
        # ....
        """
        ###############################################
        # sign up
        ############################################### 
        user_info = robot.generate_sign_up_user(random_password=True)
        robot.sign_up(user_info)
        time.sleep(5)
        robot.search_keywords(words)
        robot.simulate_browsing(words, asin, add_to_cart_probability)
        robot.exit_driver()
        """


        



    
