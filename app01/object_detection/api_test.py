import requests
from PIL import Image, ImageDraw, ImageFont

url = "https://api.va.landing.ai/v1/tools/agentic-object-detection"
path_to_image = "cell1.jpg"
your_api_key = 'OXBmYzRyMHl6bWYzYnh6ZDVzdDEwOnFnUkV6R1JVeklDM2NBYVFmemp2blhSNXpaMVJ0enZS'
files = {
  "image": open(f"{path_to_image}", "rb")
}
data = {
  "prompts": "红细胞",  #可以是红细胞，白细胞，血小板
  "model": "agentic"
}

headers = {
  "Authorization": f"Basic {your_api_key}"
}

response = requests.post(url, files=files, data=data, headers=headers)

response_data = response.json()
print(response_data)

# Load the image
image = Image.open(path_to_image)
draw = ImageDraw.Draw(image)

# 设置中文字体
try:
    font = ImageFont.truetype("simhei.ttf", 20)  # 设置中文字体文件路径和大小
except IOError:
    font = ImageFont.load_default()  # 如果字体文件不存在，使用默认字体

# Draw bounding boxes
for detection in response_data['data'][0]:
    label = detection['label']
    score = detection['score']
    bounding_box = detection['bounding_box']
    draw.rectangle(bounding_box, outline="red", width=4)  # 宽度是线框的粗细
    draw.text((bounding_box[0] + 5, bounding_box[1] + 5), f"{label} {score:.2f}", fill="red", font=font)  # 添加字体参数，调整标签位置

# Save or show the image
image.save("output.jpg")
image.show()
