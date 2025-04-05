# views/cell.py
import requests
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from io import BytesIO

config = getattr(settings, 'OBJECT_DETECTION', {})  # 使用全大写配置名称
API_KEY = config.get('API_KEY')
API_URL = config.get('URL')

def index(request):
    return render(request, 'cell_labels.html')


def detect(request):
    if request.method == 'POST':
        img_file = request.FILES.get('image')
        prompt = request.POST.get('prompt', '红细胞')

        if not img_file:
            return HttpResponse("No image uploaded", status=400)

        # 读取文件内容，避免读两次导致空
        img_data = img_file.read()
        img = Image.open(BytesIO(img_data))

        files = {'image': BytesIO(img_data)}  # 用 BytesIO 重新构造文件流
        data = {"prompts": prompt, "model": "agentic"}
        headers = {"Authorization": f"Basic {API_KEY}"}

        api_response = requests.post(API_URL, files=files, data=data, headers=headers)
        if api_response.status_code != 200:
            return HttpResponse("API error", status=500)

        resp_json = api_response.json()
        print(resp_json)  # 应该能看到输出了！

        # 开始绘图
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("simhei.ttf", 20)
        except:
            font = ImageFont.load_default()

        detections = resp_json.get('data', [[]])[0]
        for detection in detections:
            label = detection['label']
            score = detection['score']
            box = detection['bounding_box']
            if isinstance(box, list) and len(box) == 4:
                box = [int(x) for x in box]
                draw.rectangle(box, outline="red", width=4)
                draw.text((box[0] + 5, box[1] + 5), f"{label} {score:.2f}", fill="red", font=font)

        # 返回图像
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        return HttpResponse(buffer.getvalue(), content_type="image/jpeg")

    return HttpResponse("Only POST allowed", status=405)