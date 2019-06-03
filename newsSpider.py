#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import json
import re
import threading
import time
import traceback
from lxml import etree

from setting import URL_LIST, SPIDER_CONFIG
from tools import string_similar, create_mysql_conn, parse_url, parse_cmd, mysql_insert_data, parsing_time, send_msg2

last_news_time = {}
news_data = []


# 从mysql中取出最新的10条新闻数据,放入列表中
def initialize_data(sre):
    mysql_conn = create_mysql_conn(**SPIDER_CONFIG[sre]['mysql']['conn'])
    if mysql_conn:
        select_news_sql = """select * from news_flash order by id desc limit 20;"""
        cur = mysql_conn.cursor()
    try:
        cur.execute(select_news_sql)
        mysql_conn.commit()
        ret = cur.fetchall()
        if ret:
            for i in ret:
                news_data.append(i["digest"])
        else:
            print("初始化对比数据错误。。。。。")
    except:
        print(traceback.print_exc())
    finally:
        cur.close()
        mysql_conn.close()


# 不同网站的数据去重
def duplicate_removal_data(data_list):

    if not news_data:
        news_data.append(data_list[2])
        return data_list
    else:
        similar = False
        for i in news_data:
            percentage = string_similar(i, data_list[2])
            # print(percentage)
            if percentage > 0.5:
                similar = True
                # print("文本相似")
                break
        if not similar:
            news_data.append(data_list[2])
            return data_list
        else:
            return None


# 时间去重
def duplicate_removal_time1(data_time, site_name):
    if not last_news_time:
        last_news_time[site_name] = data_time
        return True
    else:
        if site_name in last_news_time.keys():
            record_time = last_news_time[site_name]
            if data_time == record_time:
                return False
            else:
                last_news_time[site_name] = data_time
                return True
        else:
            last_news_time[site_name] = data_time
            return True


def run(url_list, sre):
    for i in range(len(url_list)):
        threading.Thread(target=newsFlashSpider, name='Thread_ex' + str(i),
                        args=(url_list[i],sre)).start()
    return news_data


def newsFlashSpider(url, sre):

    r = parse_url(url)
    if r and r.status_code == 200:
        html = etree.HTML(r.text)
        if '8btc' in url:
            data = parse_8btc_html(html)
            if data:
                a = duplicate_removal_data(data)
                if a:
                    mysql_insert_data(a, sre)

        if 'wallstreetcn' in url:
            data = parse_xcong_html(r.text)
            if data:
                a = duplicate_removal_data(data)
                if a:
                    mysql_insert_data(a,sre)

        if 'hecaijing' in url:
            data = parse_hecaijing_html(html)
            if data:
                a = duplicate_removal_data(data)
                if a:
                    mysql_insert_data(a, sre)

        if 'bishijie' in url:
            data = parse_bishijie_html(html)
            if data:
                a = duplicate_removal_data(data)
                if a:
                    mysql_insert_data(a, sre)

        if "odaily" in url:
            data = parse_odaily_html(html)
            if data:
                a = duplicate_removal_data(data)
                if a:
                    mysql_insert_data(a, sre)
    else:
        content = "新闻快讯爬取：请检查当前url(%s)" % url
        send_msg2(content)

    return news_data


def parse_8btc_html(html):
    # 时间不重复就解析，标题，内容；否则不解析
    data_list = []
    try:
        publish_time = html.xpath('//div[@class="flash-wrap"]/ul/li[1]/div[1]/span/text()')[0].strip()
        if publish_time:
            publish_time = parsing_time(publish_time)
    except:
        content = "《巴比特》通过Xpath提取数据错误。。。。"
        send_msg2(content)
        return None

    title = html.xpath('//div[@class="flash-wrap"]/ul/li[1]/div[1]/a/span/text()')[0].strip()
    digest = html.xpath('//div[@class="flash-wrap"]/ul/li[1]/div[1]/div/text()')[0].strip().replace("\n", "")
    source = html.xpath('//div[@class="flash-wrap"]/ul/li[1]/div[2]/span/a/text()')[0].strip()

    if title and digest and source and len(digest) <= 500:
        data_list.append(publish_time)
        data_list.append(title)
        data_list.append(digest)
        data_list.append(source)
        return data_list
    else:
        return None


def parse_xcong_html(r):
    data_list = []
    # https://api-prod.wallstreetcn.com/apiv1/content/lives?channel=xiaocong-channel&client=pc&cursor=&limit=1&first_page=false&accept_symbols=coin
    r_text = json.loads(r)
    ts = r_text["data"]["items"][0]["display_time"]
    publish_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
    source = ''

    title = r_text["data"]["items"][0]["title"]
    digest = r_text["data"]["items"][0]["content_text"].replace("\n", "")
    if digest and digest.endswith('）'):
        p1 = re.compile(r'.*[（](.*?)[）]$', re.S)  # 最小匹配
        data = re.search(p1, digest).group(1)
        if data:
            source = data
            digest = digest.replace('（' + source + '）', "")
    else:
        source = "小葱财经"

    if title and source and len(digest) <= 500:
        data_list.append(publish_time)
        data_list.append(title)
        data_list.append(digest)
        data_list.append(source)
        return data_list
    else:
        return None


def parse_hecaijing_html(html):
    data_list = []
    try:
        publish_time = html.xpath('/html/body/div[5]/div[1]/ul/li[1]/p/span/text()')[0].strip()
        if publish_time:
            publish_time = parsing_time(publish_time)
    except:
        content = "《核财经》通过Xpath提取数据错误。。。。"
        send_msg2(content)
        return None

    title = html.xpath('/html/body/div[5]/div[1]/ul/li[1]/a/text()')[0].strip()
    digest = html.xpath('/html/body/div[5]/div[1]/ul/li[1]/div[1]/text()')[0].strip().replace("\xa0","").replace("\n", "").replace("\xa09","")
    source = "核财经"
    if title and digest and source and len(digest) <= 500:
        data_list.append(publish_time)
        data_list.append(title)
        data_list.append(digest)
        data_list.append(source)
        return data_list
    else:
        return None


def parse_bishijie_html(html):
    data_list = []
    try:
        publish_time = html.xpath('//div[@class="kuaixun_list"]/div[2]/ul[1]/span/text()')[0].strip()
        if publish_time:
            publish_time = parsing_time(publish_time)
    except:
        content = "《币世界》通过Xpath提取数据错误。。。。"
        send_msg2(content)
        return None

    title = html.xpath('//div[@class="kuaixun_list"]/div[2]/ul[1]/li/h2/a/text()')[0].strip()
    digest = html.xpath('//div[@class="kuaixun_list"]/div[2]/ul[1]/li/div/a/text()')[0].strip().replace("\n", "")
    source = "币世界"
    if title and digest and source and len(digest) <= 500:
        data_list.append(publish_time)
        data_list.append(title)
        data_list.append(digest)
        data_list.append(source)
        return data_list
    else:
        return None


def parse_odaily_html(html):
    data_list = []
    try:
        publish_time = html.xpath('//*[@id="root"]/div[3]/div[1]/div[1]/div[2]/span[1]/text()')[0].strip()
        if publish_time:
            publish_time = parsing_time(publish_time)
    except:
        content = "《星球日报》通过Xpath提取数据错误。。。。"
        send_msg2(content)
        return None

    title = html.xpath('//*[@id="root"]/div[3]/div[1]/div[1]/div[2]/h5/a/text()')[0].strip()
    digest = html.xpath('//*[@id="root"]/div[3]/div[1]/div[1]/div[2]/p/text()')[0].strip("星球日报讯").strip().replace("\n", "")
    if digest and digest.endswith('）'):
        p1 = re.compile(r'.*[（](.*?)[）]$', re.S)  # 最小匹配
        data = re.search(p1, digest).group(1)
        if data:
            source = data
            digest = digest.replace('（' + source + '）', "")
    else:
        source = "星球日报"

    if title and source and len(digest) <= 500:
        data_list.append(publish_time)
        data_list.append(title)
        data_list.append(digest)
        data_list.append(source)
        return data_list
    else:
        return None


if __name__ == "__main__":
    sre_list = parse_cmd()
    sre_list = sre_list if sre_list else ['PRE']
    for sre in sre_list:
        initialize_data(sre)
        run(URL_LIST, sre)
