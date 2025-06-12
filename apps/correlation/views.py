from django.shortcuts import render
from apps.pages.models import Pole, UF
from apps.dashboard.models import RH,Lit
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from collections import defaultdict

from statsmodels.tsa.stattools import ccf
import math
import pandas as pd


def index(request):
    poles = Pole.objects.all().order_by('libelle_standard')
    return render(request, 'correlation/index.html',{
        'poles': poles
    })

@require_GET
def get_ufs(request):
    code_pole = request.GET.get('code_pole')
    if code_pole:
        try:
            ufs = UF.objects.filter(code_pole=code_pole).order_by('libelle_standard')
            ufs_list = list(ufs.values('code_uf', 'libelle_standard'))
            return JsonResponse({
                'ufs': ufs_list,
            })
        except Pole.DoesNotExist:
            return JsonResponse({
                'ufs': [],
            })
    else:
        return JsonResponse({
                'ufs': [],
        })
    

@require_GET
def get_data(request):
    code_uf = request.GET.get('code_uf')
    code_pole = request.GET.get('code_pole')
    if code_uf and code_pole:
        try:
            rhs = RH.objects.filter(code_uf=code_uf).order_by('semaine', 'metier')
            if not rhs.exists():
                return JsonResponse({'error': 'UF not found'}, status=404)
            lits = Lit.objects.filter(code_uf=code_uf).order_by('semaine')
            if not lits.exists():
                return JsonResponse({'error': 'No lits found for this UF'}, status=404)
            
            semaine_agg = defaultdict(lambda: {'agents_abs_imprevu': 0, 'agents_abs_prevu': 0})
            for row in rhs.values('semaine', 'agents_abs_imprevu', 'agents_abs_prevu'):
                semaine = row['semaine']
                semaine_agg[semaine]['agents_abs_imprevu'] += row['agents_abs_imprevu'] or 0
                semaine_agg[semaine]['agents_abs_prevu'] += row['agents_abs_prevu'] or 0
            # Add lits_fermes_moyen from Lits, indexed by semaine
            lits_by_semaine = {l.semaine: l.lits_fermes_moyen for l in lits}
            # Prepare the aggregated data as a list of dicts
            data = [
                {
                    'semaine': semaine,
                    'agents_abs_imprevu': values['agents_abs_imprevu'],
                    'agents_abs_prevu': values['agents_abs_prevu'],
                    'lits_fermes_moyen': round(lits_by_semaine.get(semaine),2)
                }
                for semaine, values in sorted(semaine_agg.items())
            ]
            return JsonResponse({
                'data': data,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    elif code_pole:
        try:
            ufs = UF.objects.filter(code_pole=code_pole)
            ufs_list = list(ufs.values('code_uf'))
            if not ufs_list:
                return JsonResponse({'error': 'No UFs found for this pole'}, status=404)            
            return JsonResponse({
                'ufs': ufs_list,
            })
        except Pole.DoesNotExist:
            return JsonResponse({'error': 'Pole not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
    

@require_GET
def get_metiers(request):
    code_uf = request.GET.get('code_uf')
    if code_uf:
        try:
            metiers = RH.objects.filter(code_uf=code_uf).values_list('metier', flat=True).distinct()
            metiers_list = [m for m in metiers if m]
            return JsonResponse({
                'metiers': metiers_list,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

@require_GET
def get_data_metiers(request):
    code_uf = request.GET.get('code_uf')
    metiers_param = request.GET.get('metiers')
    if code_uf and metiers_param:
        try:
            rhs = RH.objects.filter(code_uf=code_uf)
            if metiers_param:
                metiers = [m for m in metiers_param.split(',') if m]
                rhs = rhs.filter(metier__in=metiers)
            rhs = rhs.order_by('semaine', 'metier')
            if not rhs.exists():
                return JsonResponse({'data': []})
            lits = Lit.objects.filter(code_uf=code_uf).order_by('semaine')
            if not lits.exists():
                return JsonResponse({'data': []})
            semaine_agg = defaultdict(lambda: {'agents_abs_imprevu': 0, 'agents_abs_prevu': 0,'abs_total': 0})
            for row in rhs.values('semaine', 'agents_abs_imprevu', 'agents_abs_prevu', 'abs_total'):
                semaine = row['semaine']
                semaine_agg[semaine]['agents_abs_imprevu'] += row['agents_abs_imprevu'] or 0
                semaine_agg[semaine]['agents_abs_prevu'] += row['agents_abs_prevu'] or 0
                semaine_agg[semaine]['abs_total'] += row['abs_total'] or 0
            lits_by_semaine = {l.semaine: l.lits_fermes_moyen for l in lits}
            data = [
                {
                    'semaine': semaine,
                    'agents_abs_imprevu': values['agents_abs_imprevu'],
                    'agents_abs_prevu': values['agents_abs_prevu'],
                    'abs_total': values['abs_total'],
                    'lits_fermes_moyen': round(lits_by_semaine.get(semaine), 2)
                }
                for semaine, values in sorted(semaine_agg.items())
            ]
            ccf_value, ccf_value2, ccf_value3 = calculer_ccf(data)
            return JsonResponse({'data': data, 'ccf_abs_total': ccf_value, 'ccf_prevu': ccf_value2, 'ccf_imprevu': ccf_value3})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    elif code_uf:
        rhs = RH.objects.filter(code_uf=code_uf).order_by('semaine', 'metier')
        if not rhs.exists():
            return JsonResponse({'error': 'UF not found'}, status=404)
        lits = Lit.objects.filter(code_uf=code_uf).order_by('semaine')
        if not lits.exists():
            return JsonResponse({'error': 'No lits found for this UF'}, status=404)
            
        semaine_agg = defaultdict(lambda: {'agents_abs_imprevu': 0, 'agents_abs_prevu': 0, 'abs_total': 0})
        for row in rhs.values('semaine', 'agents_abs_imprevu', 'agents_abs_prevu', 'abs_total'):
            semaine = row['semaine']
            semaine_agg[semaine]['agents_abs_imprevu'] += row['agents_abs_imprevu'] or 0
            semaine_agg[semaine]['agents_abs_prevu'] += row['agents_abs_prevu'] or 0
            semaine_agg[semaine]['abs_total'] += row['abs_total'] or 0
            # Add lits_fermes_moyen from Lits, indexed by semaine
        lits_by_semaine = {l.semaine: l.lits_fermes_moyen for l in lits}
            # Prepare the aggregated data as a list of dicts
        data = [
                {
                    'semaine': semaine,
                    'agents_abs_imprevu': values['agents_abs_imprevu'],
                    'agents_abs_prevu': values['agents_abs_prevu'],
                    'abs_total': values['abs_total'],
                    'lits_fermes_moyen': round(lits_by_semaine.get(semaine),2)
                }
                for semaine, values in sorted(semaine_agg.items())
            ]
        ccf_value, ccf_value2, ccf_value3 = calculer_ccf(data)
        return JsonResponse({
                'data': data,
                'ccf_abs_total': ccf_value,
                'ccf_prevu': ccf_value2,
                'ccf_imprevu': ccf_value3
            })
    else:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
    


def calculer_ccf(data):
    df = pd.DataFrame(data)

    cross_corr_values = ccf(df['abs_total'], df['lits_fermes_moyen'])
    cross_corr2= ccf(df['agents_abs_prevu'], df['lits_fermes_moyen'])
    cross_corr3= ccf(df['agents_abs_imprevu'], df['lits_fermes_moyen'])

    # Just take the first cross-correlation value for illustration
    ccf_value = cross_corr_values[0]
    ccf_value2 = cross_corr2[0]
    ccf_value3 = cross_corr3[0]

    if math.isnan(ccf_value) or math.isnan(ccf_value2) or math.isnan(ccf_value3):
        ccf_value = 0
        ccf_value2=0
        ccf_value3=0
    
    return ccf_value, ccf_value2, ccf_value3
