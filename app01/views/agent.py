from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from ..models import MedicalKnowledge  # 确保已创建模型
from django.db.models import Q
from django.utils import timezone

def search_medical_knowledge(symptoms):
    """医疗知识库检索函数"""
    keywords = [word.strip() for word in symptoms.split(',') if word.strip()]
    query = Q()
    for kw in keywords:
        query |= Q(symptoms__icontains=kw)
    return MedicalKnowledge.objects.filter(query).order_by('-id')[:3]


def ai_diagnosis(request):
    session_id = request.COOKIES.get('sessionid')
    history = cache.get(f'dialogue_{session_id}', [])

    if request.method == "POST":
        user_input = request.POST.get("symptoms", "")
        timestamp = timezone.now()

        try:
            # 1. 知识库检索
            knowledge = search_medical_knowledge(user_input)
            kb_context = "\n".join([
                f"医学知识参考：\n疾病：{k.disease}\n典型症状：{k.symptoms}"
                for k in knowledge
            ]) if knowledge else "无相关医学知识库记录"

            # 2. 构建对话链
            chat = ChatOpenAI(
                temperature=0.1,
                model="deepseek-chat",
                api_key=settings.DEEPSEEK_API_KEY,
                openai_api_base=settings.BASE_URL
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system", f"{kb_context}\n你是一位专业的全科医生，请根据对话历史进行分析：\n{{history}}"),
                ("human", "当前症状：{symptoms}\n请给出：1.可能病因 2.建议检查 3.健康建议")
            ])

            # 3. 执行调用
            chain = prompt | chat
            response = chain.invoke({
                "symptoms": user_input,
                "history": "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
            })

            # 4. 保存对话记录
            history.extend([
                {"role": "user", "content": user_input, "timestamp": timestamp},
                {"role": "assistant", "content": response.content, "timestamp": timezone.now()}
            ])
            # 限制最大历史记录数
            if len(history) > 20:
                history = history[-20:]
            cache.set(f'dialogue_{session_id}', history, timeout=3600 * 24)

            return render(request, "agent.html", {
                "history": history,
                "last_diagnosis": response.content,
                "symptoms": user_input
            })

        except Exception as e:
            return render(request, "agent.html", {
                "error": f"服务暂时不可用：{str(e)}",
                "history": history
            })

    return render(request, "agent.html", {"history": history})