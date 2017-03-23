/*
* @Author: LC
* @Date:   2016-08-23 15:16:43
* @Last Modified by:   LC
* @Last Modified time: 2016-08-26 23:20:47
*/

create database amazon;
use amazon;

create table visit_record
(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    asin CHAR(10) NOT NULL,
    date DATE NOT NULL,
    pv INT DEFAULT 0,
    cart INT DEFAULT 0,
    wish_list INT DEFAULT 0,
    keywords VARCHAR(150) NOT NULL,
    rank_page TINYINT
)ENGINE=InnoDB CHARSET=UTF8;

create index asin_date_keywords_inx on visit_record(asin, date, keywords)