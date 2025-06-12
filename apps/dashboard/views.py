from django.shortcuts import render
from apps.pages.models import UF,ETB,Pole
from apps.dashboard.models import Lit, RH
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from statistics import mean

def index(request):
    # ...existing code...
    ufh_libelles = UF.objects.values('libelle_standard', 'code_uf').distinct().order_by('libelle_standard')
    return render(request, 'dashboard/index.html', {
        'ufh_libelles': ufh_libelles,
    })

@require_GET
def get_etb(request):
    code_uf = request.GET.get('code_ufh')
    if code_uf:
        try:
            ufh= UF.objects.get(code_uf=code_uf)
            etb = ETB.objects.get(code_etb=ufh.code_etb)
            return JsonResponse({
                'etb_libelle_standard': etb.libelle_standard,
            })
        except ETB.DoesNotExist:
            return JsonResponse({
                'etb_libelle_standard': '',
            })
    else:
        return JsonResponse({
                'etb_libelle_standard': '',
            })
    
@require_GET
def get_pole(request):
    code_uf = request.GET.get('code_ufh')
    if code_uf:
        try:
            ufh = UF.objects.get(code_uf=code_uf)
            pole = Pole.objects.get(code_pole=ufh.code_pole)
            return JsonResponse({
                'pole': pole.libelle_standard,
            })
        except UF.DoesNotExist:
            return JsonResponse({
                'pole': '',
            })
    else:
        return JsonResponse({
                'pole': '',
            })
    
@require_GET
def get_lits(request):
    code_uf = request.GET.get('code_ufh')
    if code_uf:
        try:
            lits = Lit.objects.filter(code_uf=code_uf)
            total_lits_fermes = sum(l.lits_installes or 0 for l in lits)
            return JsonResponse({
                'lits': total_lits_fermes/ len(lits) if lits else 0,
            })
        except Exception:
            return JsonResponse({
                'lits': 0,
            })
    else:
        return JsonResponse({
                'lits': 0,
            })
    
@require_GET
def get_metiers(request):
    code_uf = request.GET.get('code_ufh')
    if code_uf:
        try:
            metiers = RH.objects.filter(code_uf=code_uf).values_list('metier', flat=True).distinct()
            metiers_list = [m for m in metiers if m]
            total_effectif = 0
            for metier in metiers_list:
                entries = RH.objects.filter(code_uf=code_uf, metier=metier)
                if entries.exists():
                    from statistics import mean
                    avg = mean(entries.values_list('effectif_total', flat=True))
                    distinct_entries = entries.values_list('metier', flat=True).distinct().count()
                    total_effectif += round(avg * distinct_entries) if distinct_entries else 0
            return JsonResponse({
                'metiers': metiers_list,
                'total_effectif': total_effectif,
            })
        except Exception:
            return JsonResponse({
                'metiers': [],
                'total_effectif': 0,
            })
    else:
        return JsonResponse({
                'metiers': [],
                'total_effectif': 0,
            })
    

@require_GET
def get_metier_count(request):
    code_uf = request.GET.get('code_ufh')
    metier = request.GET.get('metier')
    if code_uf and metier:
        try:
            entries = RH.objects.filter(code_uf=code_uf, metier=metier)
            avg = mean(entries.values_list('effectif_total', flat=True)) if entries else 0
            distinct_entries = entries.values_list('metier', flat=True).distinct().count()
            return JsonResponse({
                'count': round(avg*distinct_entries) if distinct_entries else 0,
            })
        except Exception:
            return JsonResponse({
                'count': 0,
            })
    else:
        return JsonResponse({
                'count': 0,
            })
    
