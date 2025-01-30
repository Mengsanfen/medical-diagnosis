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
