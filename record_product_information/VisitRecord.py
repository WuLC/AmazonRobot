# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-08-26 09:38:24
# @Last modified by:   LC
# @Last Modified time: 2017-03-23 21:23:49
# @Email: liangchaowu5@gmail.com

##################################################################
# record the detail information of product in mysql
# including: pv created by the crawler, ranking of the product. etc
# infomation of the table can be seen in create_table.sql
##################################################################

import sys
import MySQLdb
from GetProductRank import get_product_page

#infomation about mysql server
HOST = 'XXXX'
PORT = 3306
USER = 'amazon'
PASSWD = 'xxxxxx'
DB = 'amazon'
CHARSET = 'utf8'


def get_connection():
    try:
        conn = MySQLdb.connect(host=HOST,port=PORT,user=USER,passwd=PASSWD,db=DB,charset=CHARSET)
        return conn
    except Exception,e:
        print 'error while connecting to mysql'
        sys.exit()
    


def update_record(asin, keywords, field, number=1, item_keywords=None):
    """update record with Pessimistic Concurrency Control
    
    Args:
        asin (TYPE): 
        keywords (TYPE): 
        field (TYPE): 
        number (int, optional): 
    
    Returns:
        TYPE
    """
    try:
        conn = get_connection()
        conn.autocommit(False)
        cursor = conn.cursor()
        SQL = 'select %s from visit_record where asin="%s" and keywords="%s" and date=curdate() for update'%(field, asin, keywords)
        cursor.execute(SQL)
        result = cursor.fetchall()
        if not result:
            SQL = 'insert into visit_record(asin,date,keywords) values("%s", curdate(), "%s");' %(asin, keywords)
            cursor.execute(SQL)
            print 'insert new record for (%s,%s)'%(asin,keywords)

        if field == 'rank_page':
            if item_keywords:
                field_value = get_product_page(keywords, item_keywords)
            else:
                print 'Error, item deicription can not be empty'
                sys.exit(0)
        elif field=='pv' or field=='cart' or field=='wish_list':
            if result:
                field_value = int(result[0][0])
                field_value += number
            else:
                field_value = 0

        else:
            print 'ERROR: no such field %s in database'%field
            sys.exit(0)
        # update record
        SQL = 'update visit_record set %s=%s where asin="%s" and keywords="%s" and date = curdate();'%(field, field_value, asin, keywords)
        cursor.execute(SQL)
        conn.commit()
    finally:
        cursor.close()
        conn.close()



if __name__ == '__main__':
    """
    asin = 'B0131A19HP'
    keywords = 'shower+curtain+rings'
    item_keywords = 'Clean Healthy Living Roller Shower Curtain Rings - Polished Stainless Steel'
    update_record(asin, keywords, 'pv',item_keywords = item_keywords)
    """
    with open('products') as f:
        for line in f:
            asin, keywords, item_keywords = line.strip().split('#')
            update_record(asin, keywords, 'rank_page',item_keywords = item_keywords)
    

