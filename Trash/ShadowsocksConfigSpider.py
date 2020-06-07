import requests
from UserAgentList import get_useragent
from bs4 import BeautifulSoup
import json
import os
import platform
import re
import threading
import random
import time

delay_ipaddr = {}


def get_delay(ip_address):
    if platform.system() == 'Linux':
        try:
            delay = os.popen('ping {} -c 4'.format(ip_address)).readlines()[-1].split('/')[4]
            # print('{}的延迟为{}ms'.format(ip_address, delay))
            return float(delay)
        except:
            # print('{} Timeout'.format(ip_address))
            return float('99999999')
    else:
        try:
            delay = os.popen('ping {}'.format(ip_address)).readlines()[-1]
            delay = re.findall('平均 = (.*?)ms', delay)[-1]
            # print('{}的延迟为{}ms'.format(ip_address, delay))
            return float(delay)
        except:
            # print('{} Timeout'.format(ip_address))
            return float('99999999')


def get_delay_global(ipaddr):
    global delay_ipaddr
    delay_ipaddr[ipaddr] = get_delay(ipaddr)


class ShadowsocksConfig(object):
    def __init__(self, selenium_mode: bool = False):
        if selenium_mode:
            from selenium import webdriver
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            # chrome_options = Options()
            # chrome_options.add_argument('--headless')
            browser = webdriver.Chrome()
            browser.get('https://www.youneed.win/free-ss')
            print(browser.get_cookies())
            print(browser.page_source)
            print('\n\n------------------------------\n\n')
            WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[@title='放牧的风 | 技术分享，资源共享，免费SS、SSR账号、V2Ray账号，免费代理']")))
            self.page_source = browser.page_source
            print(browser.get_cookies())
            print(self.page_source)
        else:
            response = requests.get(url='https://www.youneed.win/free-ss', headers={'User-Agent': get_useragent()})
            if response.status_code == 200:
                self.page_source = response.text
                # print(self.page_source)
            else:
                raise ConnectionError('Can not get the shadowsocks config page source.')
        soup = BeautifulSoup(self.page_source, 'html.parser')
        config_list = soup.find_all('td')
        for index, content in enumerate(config_list):
            if content.string:
                config_list[index] = content.string
        single_config = []
        all_config = []
        count = 0
        for i in config_list:
            single_config.append(i)
            count += 1
            if count == 7:
                if single_config[-1] == 'US':
                    all_config.append(single_config)
                count = 0
                single_config = []
        all_config = all_config[:-5]
        # print(all_config)
        single_config_json = {}
        all_config_json = []
        for content in all_config:
            # print(content)
            single_config_json['server'] = content[1]
            single_config_json['server_port'] = int(content[2])
            single_config_json['local_address'] = '127.0.0.1'
            single_config_json['local_port'] = 1080
            single_config_json['password'] = content[3]
            single_config_json['timeout'] = 600
            single_config_json['method'] = content[4]
            all_config_json.append(single_config_json)
            single_config_json = {}
        self.config_json = all_config_json
        self.total_num = len(self.config_json)
        self.config_ipaddr = []
        for i in self.config_json:
            self.config_ipaddr.append(i['server'])

    def dump_all_json(self):
        if not os.path.exists('./ssconfig'):
            os.mkdir('ssconfig')
        with open('./ssconfig/info', mode='w', encoding='utf-8') as file:
            file.write(str(self.total_num))
        count = 0
        for i in self.config_json:
            with open('./ssconfig/ssconfig{}.json'.format(count), mode='w', encoding='utf-8') as ssconfig:
                json.dump(i, ssconfig)
                count += 1

    def dump_single_json(self, single_config):
        with open('ssconfig.json', mode='w', encoding='utf-8') as ssconfig:
            json.dump(single_config, ssconfig)

    def get_delay_ipaddr(self):
        global delay_ipaddr
        delay_ipaddr = {}
        threadpool = [threading.Thread(target=get_delay_global, args=(i,)) for i in self.config_ipaddr]
        for i in threadpool:
            i.start()
        for i in threadpool:
            i.join()
        delay_sequence = sorted(delay_ipaddr.items(), key=lambda delay: delay[1], reverse=False)
        return delay_sequence

    def get_config_by_ipaddr(self, ipaddr):
        for i in self.config_json:
            if i['server'] == ipaddr:
                return i

    def get_config_random(self):
        return random.choice(self.config_json)


if __name__ == '__main__':
    ss = ShadowsocksConfig(selenium_mode=False)
    print(ss.get_delay_ipaddr())
