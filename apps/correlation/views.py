from django.shortcuts import render
from apps.pages.models import Pole, UF
from apps.dashboard.models import RH,Lit
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from collections import defaultdict

from statsmodels.tsa.stattools import ccf
import math
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64


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
    
def clean_json(obj):
    if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_json(x) for x in obj]
    return obj
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
    rhs = RH.objects.filter(code_uf=code_uf)
    lits = Lit.objects.filter(code_uf=code_uf).order_by('semaine')
    if code_uf and metiers_param:
        metiers = metiers_param.split(',')
        if metiers:
            rhs = rhs.filter(metier__in=metiers)
        df_rh = pd.DataFrame(list(rhs.values('semaine', 'metier', 'agents_abs_imprevu','abs_total', 'agents_abs_prevu')))
        df_lits = pd.DataFrame(list(lits.values('semaine', 'lits_fermes_moyen')))
        agg_dict = {'agents_abs_imprevu': 'sum', 'agents_abs_prevu': 'sum', 'abs_total': 'sum'}
        agg_df = df_rh.groupby('semaine', as_index=False).agg(agg_dict)
        df_res = pd.merge(agg_df, df_lits[['semaine', 'lits_fermes_moyen']], on='semaine', how='left')
        ccf_value_abs_total, ccf_value_agents_abs_prevu, ccf_value_agents_abs_imprevu = calculer_ccf(df_res)
        return JsonResponse({
            'data': clean_json(df_res.to_dict(orient='records')),
            'ccf_value_abs_total': ccf_value_abs_total,
            'ccf_value_agents_abs_prevu': ccf_value_agents_abs_prevu,
            'ccf_value_agents_abs_imprevu': ccf_value_agents_abs_imprevu,
        })
    elif code_uf:
        df_rh = pd.DataFrame(list(rhs.values('semaine', 'metier', 'agents_abs_imprevu','abs_total', 'agents_abs_prevu')))
        df_lits = pd.DataFrame(list(lits.values('semaine', 'lits_fermes_moyen')))
        agg_dict = {'agents_abs_imprevu': 'sum', 'agents_abs_prevu': 'sum', 'abs_total': 'sum'}
        agg_df = df_rh.groupby('semaine', as_index=False).agg(agg_dict)
        df_res = pd.merge(agg_df, df_lits[['semaine', 'lits_fermes_moyen']], on='semaine', how='left')
        ccf_value_abs_total, ccf_value_agents_abs_prevu, ccf_value_agents_abs_imprevu = calculer_ccf(df_res)
        pivot=df_rh.pivot(index='semaine', columns='metier', values='agents_abs_prevu').reset_index()
        df_merged = pd.merge(pivot, df_lits, on='semaine', how='left')
        metiers= RH.objects.filter(code_uf=code_uf).values_list('metier', flat=True).distinct()
        metiers = [m for m in metiers if m]
        if abs(ccf_value_agents_abs_prevu)<0.5:
            return JsonResponse({
                'data': clean_json(df_res.to_dict(orient='records')),
                'ccf_value_abs_total': ccf_value_abs_total,
                'ccf_value_agents_abs_prevu': ccf_value_agents_abs_prevu,
                'ccf_value_agents_abs_imprevu': ccf_value_agents_abs_imprevu,
            })
        res=regression_lineaire(df_merged, metiers)
        graph = figure_coeffs(res)
        return JsonResponse({
            'data': clean_json(df_res.to_dict(orient='records')),
            'ccf_value_abs_total': ccf_value_abs_total,
            'ccf_value_agents_abs_prevu': ccf_value_agents_abs_prevu,
            'ccf_value_agents_abs_imprevu': ccf_value_agents_abs_imprevu,
            'regression_res': res,
            'graph': graph
        })
    else:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
    
    


def calculer_ccf(data):
    def safe_ccf(series1, series2):
        s1 = np.array(series1)
        s2 = np.array(series2)
        if np.std(s1) == 0 or np.std(s2) == 0 or len(s1) < 2:
            return 0.0
        correlation = ccf(s1, s2)
        ccf_value = correlation[0]
        return 0.0 if math.isnan(ccf_value) else ccf_value
    ccf_value_abs_total = safe_ccf(data['abs_total'], data['lits_fermes_moyen'])
    ccf_value_agents_abs_prevu= safe_ccf(data['agents_abs_prevu'], data['lits_fermes_moyen'])
    ccf_value_agents_abs_imprevu= safe_ccf(data['agents_abs_imprevu'], data['lits_fermes_moyen'])
    
    return ccf_value_abs_total, ccf_value_agents_abs_prevu, ccf_value_agents_abs_imprevu


def regression_lineaire(df, metiers=None):
    predictors = []
    metier_col_map = {}
    for metier in metiers:
        predictors.append(metier)
        metier_col_map[metier] = metier
    if not predictors:
        return {}
    X = df[predictors].values
    y = df['lits_fermes_moyen'].values
    model = LinearRegression()
    model.fit(X, y)
    coefs = {metier: float(model.coef_[i]) for i, metier in enumerate(metier_col_map.keys())}
    coefs['const'] = float(model.intercept_)
    return coefs


def figure_coeffs(data):
    plt.figure(figsize=(14,8))
    intercept = data.pop('const')
    features = list(data.keys())
    coefs = list(data.values())
    bars = plt.bar(features, coefs, color='skyblue')
    plt.axhline(0, color='gray', linewidth=0.8)

    plt.title("Effet de l'absence prévue sur fermeture de lits par métier", fontsize=22)
    plt.text(0.95, 0.95, f'Intercept: {intercept:.2f}',
            horizontalalignment='right',
            verticalalignment='top',
            transform=plt.gca().transAxes,
            fontsize=20,
            bbox=dict(facecolor='white', alpha=0.7))

    plt.xticks(rotation=20, ha='right', fontsize=18)
    plt.yticks(fontsize=20)
    plt.tight_layout()
    
    # Sauvegarde l'image en mémoire
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Encode en base64 pour l'affichage HTML
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png).decode('utf-8')
    
    plt.close()
    return graph