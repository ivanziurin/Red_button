from django.shortcuts import render
from django.db.models import Sum
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from image_manager.models import SparePartModel, StockModel
from .serializers import SparePartModelSerializer
'''
@api_view(['GET'])
def my_chart(View):
    parts = SparePartModel.objects.all()
    ser = SparePartModelSerializer(parts, many=True)
    return Response(ser.data)

'''
def my_chart(request):
    labels = []
    data = []
    min_data = []

    queryset = SparePartModel.objects.all()
    for part in queryset:
        labels.append(part.item_number)
        data.append(part.min_value)


    return render(request, 'dashboard/index.html', {
        'labels': labels,
        'data': data,
    })

'''

    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/index.html')

    def get_data(request, *args, **kwargs):
        parts = SparePartModel.objects.all()
        ser = SparePartModelSerializer(parts, many=True)
        #labels = ['jan', 'feb', 'mar', 'apr']
        #datas = [100, 50, 200, 70]
        #data = {
        #    "labels": parts.,
        #    "datas": datas,
        #}
        return JsonResponse(ser.data)

class my_chart(TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qs'] = SparePartModel.objects.all()
        return context




class my_chart(TemplateView):
    labels = ['jan', 'feb', 'mar', 'apr']
    data = [100, 50, 200, 70]
    

    queryset = StockModel.objects.values('datetime').annotate(datetime_quantity=Sum('quantity'))
    for entry in queryset:
        labels.append(entry['country__name'])
        data.append(entry['country_population'])

    return render(request, 'dashboard/index.html',
    {
        'labels': labels,
        'data': data,
    })
'''