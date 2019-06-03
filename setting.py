#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import pymysql

# 目标网站配置
URL_LIST = ["https://www.8btc.com/flash",
            "https://api-prod.wallstreetcn.com/apiv1/content/lives?channel=xiaocong-channel&client=pc&cursor=&limit=1&first_page=false&accept_symbols=coin",
            "https://www.odaily.com/newsflash",
            # "https://xcong.com/",
            "https://www.hecaijing.com/kuaixun/",
            "https://www.bishijie.com/kuaixun/"]

# 数据库配置
dn_0 = '0'
dn_2 = '2'
dn_5 = '5'


SPIDER_CONFIG = {
   'DEV': {
       'redis': {
           'redis_key': 'DEV:',
          'redis_url': 'redis://:SmallJ8Insert@192.168.0.167:7533/{dn}'
      },
      'mysql': {
          'conn': dict(
              host='118.178.255.105',
              port=4407,
              user='root',
              password='DuGu9Jian_',
              db='coindom_dev',
              charset='utf8mb4',
              cursorclass=pymysql.cursors.DictCursor,
              autocommit=True
              )
      }
  },
  'PRE': {
      'redis': {
          'redis_key': 'PRE:',
          'redis_url': 'redis://:SmallJ8Insert@114.55.105.188:7533/{dn}'
      },
      'mysql': {
         'conn': dict(
              host='118.178.255.105',
              port=4407,
              user='root',
              password='DuGu9Jian_',
              db='coindom_dev',
              charset='utf8mb4',
              cursorclass=pymysql.cursors.DictCursor,
              autocommit=True
              )
      }
  },
  'PROD': {
      'redis': {
          'redis_key': '',
          'redis_url': 'redis://:DuGu9Jian@114.55.105.188:6345/{dn}'
      },
      'mysql': {
          'conn': dict(
            host='114.55.105.188',
            port=4407,
            user='dt_writer',
            password='writer_@_pass',
            db='coindom_dev',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
            )
        }
    }
}



