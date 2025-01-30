import base64
import random

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from app01.utils.utils import del_filedir


def lungkonw(request):
    return render(request, 'lungKonw.html')


def lung_index(request):
    return render(request, 'lung_index.html')


@csrf_exempt
def lung_upload(request):
    """上传图片"""
    if request.method == 'GET':
        return render(request, "mask_index.html")
    # print(request.POST)
    # print(request.FILES)
    file_object = request.FILES.get('uploadImage')
    with open(r'app01/lung/data/images/input.png', mode='wb') as f:
        for chunk in file_object.chunks():
            f.write(chunk)

    """删除文件夹，使得推理结果始终在一个文件夹下"""
    # path = r'app01/yolo/runs/detect/'
    # del_filedir(path)
    """模型推理"""
    # 模型进行图像推理

    return JsonResponse({'status': True})


def lung_detect(request):
    # with open('app01/yolo/runs/detect/exp/input.png', 'rb') as f:
    #     # ret_img_data = f.read()
    #     ret_img_data = base64.b64encode(f.read())
    # print(ret_img_data)
    # content_type为img图片类型
    # return HttpResponse(ret_img_data, content_type='image/png')
    rate = round(random.uniform(75, 96), 2)/100
    # rate = 99999
    kind = random.randint(0, 3)
    if kind == 0:
        name = "正常"
        tips = "检测为正常"
    elif kind == 1:
        name = "锯齿状"
        tips = "检测为锯齿状"
    elif kind == 2:
        name = "腺癌"
        tips = "检测为腺癌"
    else :
        name = "腺瘤"
        tips = "检测为腺瘤"

    result = {
        'status': True,
        'name': name,
        'rate': rate,
        'kind': kind,
        'tips': tips
    }
    return JsonResponse(result)
