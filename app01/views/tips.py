from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
import http.client, urllib, json
from django.views.decorators.csrf import csrf_exempt


def health(request):
    return render(request, 'health.html')


def medical(request):
    return render(request, 'medical.html')


def protect(request):
    return render(request, 'protect.html')

@csrf_exempt
def get_medical(request):
    mname = request.POST.get("name")
    conn = http.client.HTTPSConnection('apis.tianapi.com')  # 接口域名
    params = urllib.parse.urlencode({'key': '2ff1818d76c26970a7654baaf8618ce7', 'word': mname})
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/yaopin/index', params, headers)
    tianapi = conn.getresponse()
    result = tianapi.read()
    data = result.decode('utf-8')
    dict_data = json.loads(data)
    print(dict_data)

    return JsonResponse(dict_data)

@csrf_exempt
def get_tips(request):
    try:
        # 调用天行API
        conn = http.client.HTTPSConnection('apis.tianapi.com')
        params = urllib.parse.urlencode({'key': '6167edd906a2d042b16f5e847ca72674'})
        headers = {'Content-type': 'application/x-www-form-urlencoded'}

        conn.request("POST", "/healthtip/index", params, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        json_data = json.loads(data)

        # 调试输出
        print("API响应状态码:", res.status)
        print("API返回数据:", json_data)

        # 返回标准化结构
        return JsonResponse({
            'code': 200,
            'msg': 'success',
            'data': json_data.get('result', {})
        })

    except Exception as e:
        print("接口调用异常:", str(e))
        return JsonResponse({
            'code': 500,
            'msg': '服务异常',
            'data': None
        })

@csrf_exempt
def get_air(request):   # 空气指数
    mname = request.POST.get("name")
    conn = http.client.HTTPSConnection('apis.tianapi.com')  # 接口域名
    params = urllib.parse.urlencode({'key': '6167edd906a2d042b16f5e847ca72674', 'area': mname})
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/aqi/index', params, headers)
    tianapi = conn.getresponse()
    result = tianapi.read()
    data = result.decode('utf-8')
    dict_data = json.loads(data)
    print(dict_data)

    return JsonResponse(dict_data)


@csrf_exempt
def get_coup(request):  # 健康小妙招
    keyword = request.POST.get("keyword")
    conn = http.client.HTTPSConnection('apis.tianapi.com')  # 接口域名
    params = urllib.parse.urlencode({'key': '6167edd906a2d042b16f5e847ca72674', 'word': keyword})
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/healthskill/index', params, headers)
    tianapi = conn.getresponse()
    result = tianapi.read()
    data = result.decode('utf-8')
    dict_data = json.loads(data)
    print(dict_data)

    return JsonResponse(dict_data)