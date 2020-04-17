# -*- coding: utf-8 -*-

#
# 提取广告规则，并且只提取对全域禁止的那种规则
#

# 参考 ADB 广告规则格式：https://adblockplus.org/filters

import time
import sys
import requests
import re


rules_url = [
    # 乘风 广告过滤规则
    #'https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/ABP-FX.txt',
    # 自建规则
    'https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt',
    'https://adaway.org/hosts.txt',
    'https://filters.adtidy.org/extension/chromium/filters/14.txt',
    'https://filters.adtidy.org/extension/chromium/filters/11.txt',
    'https://gitee.com/halflife/list/raw/master/ad.txt',
    'https://gitee.com/xinggsf/Adblock-Rule/raw/master/rule.txt',
    'https://www.fanboy.co.nz/r/fanboy-ultimate.txt',
    'https://gitee.com/xinggsf/Adblock-Rule/raw/master/mv.txt',
    'https://raw.githubusercontent.com/user1121114685/koolproxyR_rule_list/master/kpr_our_rule.txt',
    'https://raw.githubusercontent.com/jdlingyu/ad-wars/master/hosts',
    'http://sbc.io/hosts/alternates/fakenews-gambling-porn-social/hosts',
    'https://raw.githubusercontent.com/vokins/yhosts/master/hosts',
    'https://hosts.nfz.moe/full/hosts',
    'https://raw.githubusercontent.com/Goooler/1024_hosts/master/hosts',
    'https://gitee.com/privacy-protection-tools/anti-ad/raw/master/easylist.txt',
    'https://raw.githubusercontent.com/vokins/yhosts/master/data/tvbox.txt',
    'https://raw.githubusercontent.com/lack006/Android-Hosts-L/master/hosts_files/2017_hosts/AD',
    'https://raw.githubusercontent.com/easonjim/blackhosts/master/hosts'
]

rule = ''

# contain both domains and ips
domains = []


for rule_url in rules_url:
    print('loading... ' + rule_url)

    # get rule text
    success = False
    try_times = 0
    r = None
    while try_times < 5 and not success:
        r = requests.get(rule_url)
        if r.status_code != 200:
            time.sleep(1)
            try_times = try_times + 1
        else:
            success = True
            break

    if not success:
        sys.exit('error in request %s\n\treturn code: %d' % (rule_url, r.status_code) )

    rule = rule + r.text + '\n'


# parse rule
rule = rule.split('\n')
for row in rule:
    row = row.strip()
    row0 = row

    # 处理广告例外规则

    if row.startswith('@@'):
        i = 0
        while i < len(domains):
            domain = domains[i]
            if domain in row:
                del domains[i]
            else:
                i = i + 1

        continue


    # 处理广告黑名单规则

    # 直接跳过
    if row=='' or row.startswith('!') or "$" in row or "##" in row:
        continue

    # 清除前缀
    row = re.sub(r'^\|?https?://', '', row)
    row = re.sub(r'^\|\|', '', row)
    row = row.lstrip('.*')

    # 清除后缀
    row = row.rstrip('/^*')
    row = re.sub(r':\d{2,5}$', '', row)  # 清除端口

    # 不能含有的字符
    if re.search(r'[/^:*]', row):
        print('ignore: '+row0)
        continue

    # 只匹配域名或 IP
    if re.match(r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,9}$', row) or re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', row):
        domains.append(row)

print('done.')


# write into files

file_ad = sys.stdout
try:
    if sys.version_info.major == 3:
        file_ad = open('ad.list', 'w', encoding='utf-8')
    else:
        file_ad = open('ad.list', 'w')
except:
    pass

file_ad.write('# adblock rules refresh time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')

domains = list( set(domains) )
domains.sort()

for item in domains:
    file_ad.write(item + '\n')
