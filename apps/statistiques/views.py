from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

from apps.hebergement_hors_uf.models import EM,Matrice_EM_UF,export_UF
from apps.hospitalisation.models import Hospitalisation
from .models import ChargeEM



@login_required
def statistiques_globales(request):
    ems = list(EM.objects.all().values('code_em', 'libelle_em'))
    context = {
        'ems': ems
    }
    return render(request, 'statistiques/statistiques_globales.html', context)

@require_GET
def api_global_stats(request):
    total_ems = EM.objects.count()
    total_sejours = Hospitalisation.objects.count()
    valid_pairs = set(Matrice_EM_UF.objects.values_list('code_em', 'code_uf'))
    hebergements = Hospitalisation.objects.exclude(code_uf__isnull=True)
    total_hebergements = 0
    for h in hebergements.values('code_em', 'code_uf'):
        if (h['code_em'], h['code_uf']) not in valid_pairs:
            total_hebergements += 1
    return JsonResponse({
        'total_ems': total_ems,
        'total_sejours': total_sejours,
        'total_hebergements': total_hebergements
    })

@require_GET
def api_em_stats(request):
    code_em = request.GET.get('code_em')
    if not code_em:
        return JsonResponse({'error': 'Missing code_em'}, status=400)
    sejours = Hospitalisation.objects.filter(code_em=code_em).count()
    # Get all code_uf for this code_em in Matrice_EM_UF
    valid_ufs = set(Matrice_EM_UF.objects.filter(code_em=code_em).values_list('code_uf', flat=True))
    hebergements = Hospitalisation.objects.filter(code_em=code_em).exclude(code_uf__isnull=True)
    hebergement_count = 0
    for h in hebergements.values_list('code_uf', flat=True):
        if h not in valid_ufs:
            hebergement_count += 1
    return JsonResponse({
        'sejours': sejours,
        'hebergements': hebergement_count
    })

@require_GET
def get_charge_em(request):
    code_em = request.GET.get('code_em')
    if not code_em:
        return JsonResponse({'error': 'Missing code_em'}, status=400)

    # Only select the fields you need to avoid unknown column errors
    data = ChargeEM.objects.filter(code_em=code_em).order_by('date').values('date', 'charge')
    result = [
        {
            'date': row['date'].strftime('%Y-%m-%d') if row['date'] else str(row['date']),
            'charge_em': row['charge']
        }
        for row in data
    ]
    return JsonResponse(result, safe=False)
    
    
