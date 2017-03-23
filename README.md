
# 模拟访问亚马逊商品的爬虫

`AmazonRobot` 是通过 `python` 实现的一个通过脚本自动访问[Amazon][1]上的商品的爬虫程序。主要实现了用户注册、根据给出的搜索词语和商品的 `asin` 号进行搜索并访问商品、按照一定概率将商品加入购物车等。同时通过动态修改UA ,维护代理池， 控制爬取速率防止被识别出是爬虫。由于需要解析网页的 JS 代码，整个代码主要依靠 `selenium` 来解析 JS 代码。

用到的数据库有 `Redis` 和 `MySQL`，`Redis` 主要用于存储代理池、用于注册的一些用户信息(姓名，电话，地址，visa卡等)；`MySQL`用于存储被访问的商品的一些信息（asin号，访问日期，日pv量，商品的排名等）。**需要先在代码中指定这两个数据库的地址**。


除了 `selenium`， 还依赖的第三方库有：`redis`, `MySQLdb`, `requests`, `bs4`,  `user_agent`；python版本为2.7

整个代码的结构如下：
```
├── Main.py                         # 主程序入口
├── Robot.py                        # 模拟访问的Robot类
├── get_proxy_and_user_information  # 抓取代理和用户信息，存入Redis
│   ├── ConnectRedis.py             # 需要在该文件中指定 Redis 数据库的地址
│   ├── GetProxy.py
│   ├── GetUserInfo.py
│   ├── IgnoreWarnings.py
│   ├── __init__.py
├── record_product_information      # 更新商品在 MySQL 中的信息
│   ├── create_table.sql
│   ├── GetProductRank.py
│   ├── VisitRecord.py              # 需要在该文件中指定 MySQL 数据库的地址
│   ├── __init__.py
└── scripts                         
    ├── Alarm.py                    # 用于检测主机是否宕机的脚本
    └── ChangeMacAddress.py         # 更改主机 mac 地址      
```

上面最后的一个文件`ChangeMacAddress.py`可用于更改主机 mac 地址（目前支持 ubuntu 16.0 和 centos6.0），原来是为了防止被识别出是爬虫而写的，但是后来想想实际上并不能起到这个作用。从计算机网络的知识可知，数据包的mac地址每经过一次转发mac地址都会改变，原因是以太网在链路层中通过arp广播建立arp表用于 IP 和 mac 地址的映射关系，然后进行转发，当数据包从链路层出来后，实际上是根据 mac 地址去查找目的主机去转发的，因此数据包在转发过程中IP地址不变(NAT之类的除外)，而mac地址每转发一次就改变一次。显然，我们的网络跟亚马逊的网络不是直连的，因此mac地址肯定会改变多次。

最后，通过 `selenium` 实现的爬虫实际上是非常消耗内存和CPU的，所以这样访问的效率会非常低下，在实验过程中对于流量较小的商品曾试过一周内将其从第五页推到首页，但是对于流量较大的商品作用就很小了。建议调试的时候带 GUI ，而在服务器运行的时候通过 `xvfb` 替代GUI，同时结合 `Ansible` 等实现主机群管理。

  [1]: https://www.amazon.com/