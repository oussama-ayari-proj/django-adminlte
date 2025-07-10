from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import Prediction
from apps.pages.models import UF

# Create your views here.

def index(request):
    ufs = UF.objects.order_by('libelle_standard')
    ufs_list = list(ufs.values('code_uf', 'libelle_standard'))
    return render(request, 'predictions/index.html', {'ufs': ufs_list})

def get_predictions_stats(request):
    code_uf = request.GET.get('code_uf')

    data = Prediction.objects.filter(code_uf=code_uf).values('date', 'pred', 'pred_exog').order_by('date')
    if not data:
        return HttpResponse("No data found for the given UF code.", status=404)
    
    # Convert queryset to list of dictionaries and format date
    data_list = []
    for row in data:
        row = dict(row)
        if row['date']:
            row['date'] = row['date'].strftime('%Y-%m-%d')
        data_list.append(row)
    
    return JsonResponse(data_list, safe=False)
