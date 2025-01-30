import json
from app01.utils.utils import del_filedir
from app01.yolo import detect

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

import base64


def mask_index(request):
    return render(request, "mask_index.html")


@csrf_exempt
def mask_upload(request):
    """上传图片"""
    if request.method == 'GET':
        return render(request, "mask_index.html")
    # print(request.POST)
    # print(request.FILES)
    file_object = request.FILES.get('uploadImage')
    with open(r'app01/yolo/data/images/input.png', mode='wb') as f:
        for chunk in file_object.chunks():
            f.write(chunk)

    """删除文件夹，使得推理结果始终在一个文件夹下"""
    path = r'app01/yolo/runs/detect/'
    del_filedir(path)
    """模型推理"""
    detect.run()
    return JsonResponse({'status': True})


def mask_img(request):
    with open('app01/yolo/runs/detect/exp/input.png', 'rb') as f:
        # ret_img_data = f.read()
        ret_img_data = base64.b64encode(f.read())
        # print(ret_img_data)
    # content_type为img图片类型
    # return HttpResponse(ret_img_data, content_type='image/png')
    return HttpResponse(ret_img_data, content_type='image/png')
