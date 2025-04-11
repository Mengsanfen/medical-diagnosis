# -*- coding: utf-8 -*-
import http.client, urllib, json
conn = http.client.HTTPSConnection('apis.tianapi.com')  #接口域名
params = urllib.parse.urlencode({'key':'6167edd906a2d042b16f5e847ca72674','area':'延安'})
headers = {'Content-type':'application/x-www-form-urlencoded'}
conn.request('POST','/aqi/index',params,headers)
tianapi = conn.getresponse()
result = tianapi.read()
data = result.decode('utf-8')
dict_data = json.loads(data)
print(dict_data)