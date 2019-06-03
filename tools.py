#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import json
import sys
import getopt
import datetime
import traceback
# from redis import StrictRedis
import time
import pymysql as pymysql
import requests
from retrying import retry
import difflib
from setting import SPIDER_CONFIG

news_data = {}


# 文本比对去重
def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def parse_cmd():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:")
    except getopt.GetoptError:
        print('')
        sys.exit()
    for opt, arg in opts:
        if opt in ['-h']:
            print('-h help')
            print('-p DEV,PRE,PROD')
        elif opt in ['-p']:
            return arg.upper().split(',')

# 创建数据库连接
def create_mysql_conn(**kwargs):
     count = 0
     while 1:
         try:
            return pymysql.connect(**kwargs)
         except:
                print(traceback.print_exc())
                if count >= 3:
                    return None
                count += 1
                time.sleep(5)


def mysql_insert_data(news, sre):
    mysql_conn = create_mysql_conn(**SPIDER_CONFIG[sre]['mysql']['conn'])

    if mysql_conn:
        # create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts_now))
        # create_date = time.strftime("%Y%m%d", time.localtime(ts_now))

        insert_news_sql = """insert into news_flash (publish_time, title, digest, source) values ('%s', '%s', '%s', '%s');"""
        cur = mysql_conn.cursor()
    try:
        data = insert_news_sql % tuple(news)
        cur.execute(data)
        mysql_conn.commit()
        print("插入数据成功 %s" % news[1])
    except:
        print(traceback.print_exc())
    finally:
        cur.close()
        mysql_conn.close()


# 正式的钉钉通知群
def send_msg(data):
    url = "https://javascriptisinjdkbp1nc9llc1h566rg8uyw2.coin-1.com:444/app/alert"
    try:
        requests.post(url, data={'content': data, 'type': 'DATA_NOTIFY'})
    except Exception as e:
        print("发送监控报告失败......")
    print("监控报告发送成功......%s" % data)


# 测试的钉钉通知群
def send_msg2(content):
    url = "https://oapi.dingtalk.com/robot/send?access_token=4de6093718c51e21d155b0e33e6ffa81b55f16443c32c6841dbed4daf6982706"
    data1 = {
        "msgtype": "text",
        "text": {
            "content": '监控报告：%s' % content
        },
        "at":{}
    }
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(data1))
        r.encoding = 'utf-8'
    except Exception as e:
        print("发送监控报告失败......")
    print("监控报告发送成功......%s" % content)


def parsing_time(str_time):
    # 当地时间
    nowTime = datetime.datetime.now().strftime('%Y-%m-%d') + " " + str_time + ":00"
    return nowTime

def string_toDatetime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")


#最大重试3次，3次全部报错，才会报错
@retry(stop_max_attempt_number=3)
def _parse_url(url):
    #超时的时候回报错并重试
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
               "Connection": "close"
               }

    requests.packages.urllib3.disable_warnings()
    response = requests.get(url, headers=headers, timeout=30, verify=False)
    #状态码不是200，也会报错并重试
    assert response.status_code == 200
    return response

def parse_url(url):
    try:
        response = _parse_url(url)
    except Exception as e:
        response = None
    return response


# 创建redis连接
# def create_redis_conn(url, dn=None):
#     count = 0
#     while 1:
#           try:
#               if dn:
#                   return StrictRedis.from_url(url.format(dn=dn))
#               else:
#                   return StrictRedis.from_url(url)
#           except:
#               print(traceback.print_exc())
#               if count >= 3:
#                   return None
#               count += 1
#               time.sleep(5)


if __name__ == "__main__":
    pass
