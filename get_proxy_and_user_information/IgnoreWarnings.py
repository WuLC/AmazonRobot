# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-07-11 22:31:51
# @Last modified by:   LC
# @Last Modified time: 2016-08-14 09:29:00
# @Email: liangchaowu5@gmail.com

###########################################################
# function: ignore the warnings when visiting https website
###########################################################

import requests


from requests.packages.urllib3.exceptions import  InsecurePlatformWarning,InsecureRequestWarning, SubjectAltNameWarning, SNIMissingWarning

def ignore_warnings():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    requests.packages.urllib3.disable_warnings(SubjectAltNameWarning)
    requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
    requests.packages.urllib3.disable_warnings(SNIMissingWarning)