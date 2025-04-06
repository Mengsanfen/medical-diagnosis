from django.db import models
from django.db.models import Q

class MedicalKnowledge(models.Model):
    disease = models.CharField("疾病名称", max_length=100)
    symptoms = models.TextField("典型症状")
    check_items = models.TextField("建议检查")
    advice = models.TextField("处理建议")

    def __str__(self):
        return self.disease

    @classmethod
    def search(cls, symptoms):
        keywords = [word.strip() for word in symptoms.split(',') if word.strip()]
        query = Q()
        for kw in keywords:
            query |= Q(symptoms__icontains=kw)
        return cls.objects.filter(query).order_by('-id')[:3]