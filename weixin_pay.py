#!/usr/bin/env python
# coding=utf-8

"""
xml2json:https://github.com/hay/xml2json
log_debug, log_info 相当于print 
"""

from flask import current_app
from aladin.helpers import log_debug, log_info
from hashlib import md5
import requests, time, json
from xml.etree import ElementTree
from xml2json import xml2json
import optparse


class WeiXinPay():
    """微信支付，返回回客户端需要参数
    """
    def __init__(self, order_id, body, total_fee, nonce_str, spbill_create_ip='8.8.8.8'):
        """
        :param order_id: 订单ID
        :param body: 订单信息
        :param total_fee: 订单金额
        :param nonce_str: 32位内随机字符串
        :param spbill_create_ip: 客户端请求IP地址
        """
        self.params = {
            'appid': current_app.config['APPID'], 
            'mch_id': current_app.config['MCHID'],
            'nonce_str': nonce_str,
            'body': body,
            'out_trade_no': str(order_id),
            'total_fee': str(int(total_fee)),
            'spbill_create_ip': spbill_create_ip,
            'trade_type': 'APP',
            'notify_url': current_app.config['WEIXIN_NOTIFY_URL']
        }


        self.url = 'https://api.mch.weixin.qq.com/pay/unifiedorder' # 微信请求url
        self.error = None

    def key_value_url(self, value):
        """将将键值对转为 key1=value1&key2=value2
        """
        key_az = sorted(value.keys())
        pair_array = []
        for k in key_az:
            v = value.get(k, '').strip()
            v = v.encode('utf8')
            k = k.encode('utf8')
            log_info('%s => %s' % (k,v))
            pair_array.append('%s=%s' % (k, v))

        tmp = '&'.join(pair_array)
        log_info("key_value_url ==> %s " %tmp)
        return tmp

    def get_sign(self, params):
        """生成sign
        """
        stringA = self.key_value_url(params)
        stringSignTemp = stringA + '&key=' + current_app.config['APIKEY'] # APIKEY, API密钥，需要在商户后台设置
        log_info("stringSignTemp ==> %s" % stringSignTemp)
        sign = (md5(stringSignTemp).hexdigest()).upper()
        params['sign'] = sign
        log_info("sign ==> %s" % sign)

    def get_req_xml(self):
        """拼接XML
        """
        self.get_sign(self.params)
        xml = "<xml>"
        for k, v in self.params.items():
            v = v.encode('utf8')
            k = k.encode('utf8')
            xml += '<' + k + '>' + v + '</' + k + '>'
        xml += "</xml>"
        log_info(xml)
        return xml


    def get_prepay_id(self):
        """
        请求获取prepay_id
        """
        xml = self.get_req_xml()
        headers = {'Content-Type': 'application/xml'}
        r = requests.post(self.url, data=xml, headers=headers)
        log_info(r.text)
        log_info("++++++++++++++++++++++++++")
        re_xml = ElementTree.fromstring(r.text.encode('utf8'))
        xml_status = re_xml.getiterator('result_code')[0].text
        log_info("result_code ==> %s" % xml_status)
        if xml_status != 'SUCCESS':
            self.error = u"连接微信出错啦！"
            return
        prepay_id = re_xml.getiterator('prepay_id')[0].text

        self.params['prepay_id'] = prepay_id
        self.params['package'] = 'Sign=WXPay'
        self.params['timestamp'] = str(int(time.time()))


    def re_finall(self):
        """得到prepay_id后再次签名，返回给终端参数
        """
        self.get_prepay_id()
        if self.error:
            return

        sign_again_params = {
            'appid': self.params['appid'],
            'noncestr': self.params['nonce_str'],
            'package': self.params['package'],
            'partnerid': self.params['mch_id'],
            'timestamp': self.params['timestamp'],
            'prepayid': self.params['prepay_id']
        }
        self.get_sign(sign_again_params)
        self.params['sign'] = sign_again_params['sign']

        # 移除其他不需要返回参数
        for i in self.params.keys():
            if i not in [
                'appid', 'mch_id', 'nonce_str',
                         'timestamp', 'sign', 'package', 'prepay_id']:
                self.params.pop(i)

        return self.params



class WeiXinResponse(WeiXinPay):
    """
    微信签名验证
    """
    def __init__(self, xml):
        """
        :param xml: 支付成功回调的XML
        """
        self.xml = xml
        options = optparse.Values({"pretty": False})
        self.xml_json = json.loads(xml2json(self.xml, options))['xml']
        self.sign = self.xml_json.get('sign', '')

    def verify(self):
        """验证签名"""

        self.xml_json.pop('sign')
        self.get_sign(self.xml_json)
        if self.sign != self.xml_json['sign']:
            log_info("signValue:%s !=  sing:%s" % (self.xml_json['sign'], self.sign))
            return False

        return True


























