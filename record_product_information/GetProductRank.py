# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-08-25 22:19:42
# @Last modified by:   LC
# @Last Modified time: 2016-09-02 22:09:13
# @Email: liangchaowu5@gmail.com

from selenium import webdriver
from bs4 import BeautifulSoup


# PhantomJS 无法完全解释，某些项无法获取
#driver = webdriver.PhantomJS(executable_path = r'H:/PythonModule/phantomjs/phantomjs-2.1.1-windows/bin/phantomjs.exe')
#item_keywords = 'Bestfy(TM) 2Pack 10FT Nylon Braided Lightning Cable'

def get_product_page(search_keywords, item_keywords):
    """find the page of an item described by item_keywords when searching with search_keywords
    
    Args:
        search_keywords (str): keywords to search items, joined by '+'
        item_keywords (str): words to describe an item, part of title of the item
    
    Returns:
        
    """
    driver = webdriver.Firefox()
    found = False
    page = -1
    try:
        for i in xrange(1,21):
            target_url = 'https://www.amazon.com/s/ref=sr_pg_%s?page=%s&keywords=%s&ie=UTF8'%(i, i, search_keywords)
            driver.get(target_url)
            text = driver.page_source
            soup = BeautifulSoup(text, 'lxml')
            titles = soup.find_all('h2')
            for title in titles:
                if item_keywords in title.get('data-attribute', ''):
                    print 'Page %s: Found'%i
                    found = True
                    print title.get('data-attribute')
                    print target_url
                    break
            if found:
                page = i
                break
            print 'Page %s: Not Found'%i
        return page
    except Exception, e:
        print e.message
    finally:
        driver.quit()

if __name__ == '__main__':
    search_keywords = 'lightning+cable'
    item_keywords = 'Bestfy(TM) 2Pack 10FT Nylon Braided Lightning Cable 8Pin to USB Charging Cable'

    search_keywords = 'shower+curtain+rings'
    item_keywords = 'Clean Healthy Living Roller Shower Curtain Rings - Polished Stainless Steel'

    search_keywords = 'shower+curtain+rings'
    item_keywords = 'Carnation Home Fashions Rococo Ceramic Resin Shower Curtain Hook, Brown-set of 12'
    get_product_page(search_keywords, item_keywords)


