# ai.py
from django.shortcuts import render
from django.http import JsonResponse

def ai_chat(request):
    """AI问诊聊天界面"""
    return render(request, 'ai_chat.html')

def ai_process(request):
    """处理用户问诊请求"""
    if request.method == 'POST':
        symptoms = request.POST.get('symptoms', '')
        # 这里可以接入实际的大模型API
        response = {
            'diagnosis': '初步判断为呼吸道感染，建议多休息、多喝水，若发热超过38.5℃请及时就医',
            'advice': ['服用退烧药（如布洛芬）', '避免冷空气刺激', '3日内症状未缓解需就诊']
        }
        return JsonResponse(response)
    return JsonResponse({'error': '无效请求'}, status=400)