"""epidemic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app01.views import index, mask, screen, lung, tips, chat

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', index.index),
    #ai问诊
    path('ai-chat/', chat.ai_chat, name='ai_chat'),  # AI问诊主界面
    path('ai-chat/process/', chat.ai_process, name='ai_process'),  # 问诊处理接口
    #口罩检测==》细胞检测
    path('mask/', mask.mask_index),
    path('mask/upload/', mask.mask_upload),
    path('mask/img/', mask.mask_img),

    # 白肺分类==》癌症图像分类
    path('screen/', screen.index),
    path('lungkonw/', lung.lungkonw),
    path('lung/', lung.lung_index),
    path('lung/upload/', lung.lung_upload),
    path('lung/detect/', lung.lung_detect),
    # 药品科普
    path('medical/', tips.medical),
    path('medical/data/', tips.get_medical),
    path('health/', tips.health),
    path('protect/', tips.protect),

]
