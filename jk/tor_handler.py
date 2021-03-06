
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import socks
import socket
from stem import Signal
from stem.control import Controller
from urllib3 import PoolManager, Retry, Timeout, ProxyManager

import logging
logger = logging.getLogger('jk')

class PlainUtility():

    def __init__(self):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers = {'User-Agent': user_agent}
        self.ip_url = 'http://icanhazip.com/'
        retries = Retry(connect=5, read=25, redirect=5)
        self.agent = PoolManager(
            10, retries=retries, timeout=Timeout(total=30.0))

    def current_ip(self):
        return self.request(self.ip_url)

    def request(self, url):
        r = self.agent.request('GET', url)
        if r.status == 200:
            return r.data
        else:
            logger.error('status %s' % r.status)


class TorUtility():

    def __init__(self):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers = {'User-Agent': user_agent}
        self.ip_url = 'http://icanhazip.com/'
        retries = Retry(connect=5, read=25, redirect=5)
        self.agent = ProxyManager(
            'http://localhost:8118/', retries=retries, timeout=Timeout(total=60.0))

    def renewTorIdentity(self, passAuth):
        try:
            s = socket.socket()
            s.connect(('localhost', 9051))
            s.send('AUTHENTICATE "{0}"\r\n'.format(passAuth))
            resp = s.recv(1024)

            if resp.startswith('250'):
                s.send("signal NEWNYM\r\n")
                resp = s.recv(1024)

                if resp.startswith('250'):
                    logger.info("Identity renewed")
                else:
                    logger.info("response 2:%s" % resp)

            else:
                logger.info("response 1:%s" % resp)

        except Exception as e:
            logger.error("Can't renew identity: %s" % e)

    def renew_connection(self):
        with Controller.from_port(port=9051) as controller:
            controller.authenticate('natalie')
            controller.signal(Signal.NEWNYM)

        logger.info('*' * 50)
        logger.info('\t' * 6 + 'Renew TOR IP: %s' %
                         self.request(self.ip_url))
        logger.info('*' * 50)

    def request(self, url):
        r = self.agent.request('GET', url)
        if r.status == 200:
            return r.data
        elif r.status == 403:
            self.renew_connection()
        else:
            logger.error('status %s' % r.status)
        return ''

    def current_ip(self):
        return self.request(self.ip_url)

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class SeleniumUtility():

    def __init__(self, use_tor=True):
        self.ip_url = 'http://icanhazip.com/'
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
            "(KHTML, like Gecko) Chrome/15.0.87"
        )
        # DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = user_agent
        service_args = [
            '--proxy=127.0.0.1:8118',  # provixy proxy
            '--proxy-type=http',
        ]
        if use_tor:
            self.agent = webdriver.PhantomJS(
                'phantomjs', service_args=service_args, desired_capabilities=dcap)
        else:
            self.agent = webdriver.PhantomJS(
                'phantomjs', desired_capabilities=dcap)
        self.agent.set_page_load_timeout(120)

    def request(self, url):
        for i in xrange(1, 4):
            try:
                self.agent.get(url)
                return self.agent.page_source
            except:
                logger.error('#%d request timeout' % i)

    def __del__(self):
        self.agent.quit()
