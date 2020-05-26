# -*- coding: utf-8 -*-

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for, current_app, flash
import re
import os
import json
from iota import Iota
from iota import ProposedTransaction
from iota import Address
from iota import Tag
from iota import TryteString
from iota.crypto.types import Seed
import uuid


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='homepage.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def judge_phone(phone):
    if re.match(
            '(9[8543210]|8[6421]|6[6543210]|5[87654321]|4[987654310]|3[9643210]|2[70]|7|1)\d{1,11}$',
            phone) != None:
        return True
    return False


def judge_email(email):
    rp = re.compile('^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$')
    emailMatch = rp.match(email)

    if emailMatch:
        return True
    else:
        return False


def judge_seed(seed):
    if len(seed) == 81:
        return True
    else:
        return False


def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def random_avatar():
    return uuid.uuid4().hex


ip = os.getenv('IP', 'http://127.0.0.1:14265')


def getNewSeed():
    return str(Seed.random())


def getNewAddress(seed):
    # 获取IOTA api函数接口
    api = Iota(ip, seed=seed, testnet=True)
    # 设置信息传输安全等级
    security_level = os.getenv('SECURITY_LEVEL', 1)
    # 获取可用的交易地址
    address = api.get_new_addresses(index=0, count=1,
                                    security_level=security_level)['addresses'][0]
    return str(address)


def transaction(seed, address, form):
    # 获取IOTA api函数接口
    api = Iota(ip, seed=seed, testnet=True)
    # 将要传送的json数据字符串化
    stringified = json.dumps(form)
    # 转换数据编码格式
    message = TryteString.from_unicode(stringified)
    # 对交易进行打包
    tx = ProposedTransaction(
        address=Address(address),
        message=message,
        value=0
    )
    # 发送交易并获得交易结果
    result = api.send_transfer(transfers=[tx])
    # 取出返回的hash值
    tail_transaction_hash = result['bundle'].tail_transaction.hash
    return str(tail_transaction_hash)


def getInformation(hash_value, seed=None):
    # 获取IOTA api函数接口
    if seed is None:
        api = Iota(ip, testnet=True)
    else:
        api = Iota(ip, seed=seed, testnet=True)
    # 获取交易捆绑
    bundle = api.get_bundles(hash_value)
    # 读取交易信息
    message = bundle['bundles'][0].tail_transaction.signature_message_fragment
    # 将信息转成json数据格式并返回
    jsonData = json.loads(message.decode())
    return jsonData


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


def cmp_json(src_json, dst_json):
    equal = True
    for key in src_json.keys():
        if key not in dst_json:
            equal = False
            break
        else:
            src_value = src_json[key]
            dst_value = dst_json[key]

            if src_value != dst_value:
                equal = False
                break

    return equal
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in current_app.config['BLUELOG_ALLOWED_IMAGE_EXTENSIONS']