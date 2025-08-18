from django.shortcuts import render
from apps.pages.models import Pole, UF
from apps.correlation.models import RH,Lit
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

import random
import colorsys


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
    metier_graph_option=request.GET.get('metier_graph_option')

    if code_uf and metiers_param:
        print("inside first if")
        metiers = metiers_param.split(',')
        if metiers:
            rhs = rhs.filter(metier__in=metiers)
        df_rh = pd.DataFrame(list(rhs.values('semaine', 'metier', 'agents_abs_imprevu','abs_total', 'agents_abs_prevu')))
        df_lits = pd.DataFrame(list(lits.values('semaine', 'lits_fermes_moyen')))
        
        # Extract week number from semaine (format: "4 - 2023")
        if not df_lits.empty:
            df_lits['week_number'] = df_lits['semaine'].apply(lambda x: int(x.split(' - ')[0]) if x and ' - ' in str(x) else 0)
            df_lits['semaine'] = df_lits['week_number']
            df_lits.drop(columns=['week_number'], inplace=True)

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
    if code_uf:
        print("inside second if")
        df_rh = pd.DataFrame(list(rhs.values('semaine', 'metier', 'agents_abs_imprevu','abs_total', 'agents_abs_prevu','famille_metier', 'sous_famille_metier')))
        df_lits = pd.DataFrame(list(lits.values('semaine', 'lits_fermes_moyen')))
        
        # Extract week number from semaine (format: "4 - 2023")
        if not df_lits.empty:
            df_lits['week_number'] = df_lits['semaine'].apply(lambda x: int(x.split(' - ')[0]) if x and ' - ' in str(x) else 0)
            df_lits['semaine'] = df_lits['week_number']
            df_lits.drop(columns=['week_number'], inplace=True)

        agg_dict = {'agents_abs_imprevu': 'sum', 'agents_abs_prevu': 'sum', 'abs_total': 'sum'}
        agg_df = df_rh.groupby('semaine', as_index=False).agg(agg_dict)
        df_res = pd.merge(agg_df, df_lits[['semaine', 'lits_fermes_moyen']], on='semaine', how='left')
        ccf_value_abs_total, ccf_value_agents_abs_prevu, ccf_value_agents_abs_imprevu = calculer_ccf(df_res)
        if abs(ccf_value_agents_abs_prevu)<0.5:
            return JsonResponse({
                'data': clean_json(df_res.to_dict(orient='records')),
                'ccf_value_abs_total': ccf_value_abs_total,
                'ccf_value_agents_abs_prevu': ccf_value_agents_abs_prevu,
                'ccf_value_agents_abs_imprevu': ccf_value_agents_abs_imprevu,
            })
        res_metier, graph_metier,r2_score_metier = regression_call(df_rh,df_lits,'metier',code_uf, metier_graph_option)
        res_famille, graph_famille, r2_score_famille = regression_call(df_rh,df_lits, 'famille_metier', code_uf, metier_graph_option)
        res_sous_famille, graph_sous_famille, r2_score_sous_famille = regression_call(df_rh,df_lits, 'sous_famille_metier', code_uf, metier_graph_option)

        return JsonResponse({
            'data': clean_json(df_res.to_dict(orient='records')),
            'ccf_value_abs_total': ccf_value_abs_total,
            'ccf_value_agents_abs_prevu': ccf_value_agents_abs_prevu,
            'ccf_value_agents_abs_imprevu': ccf_value_agents_abs_imprevu,
            'regression_res_metier': res_metier,
            'graph_metier': graph_metier,
            'regression_res_famille': res_famille,
            'graph_famille': graph_famille,
            'regression_res_sous_famille': res_sous_famille,
            'graph_sous_famille': graph_sous_famille,
            'r2_score_metier': r2_score_metier,
            'r2_score_famille': r2_score_famille,
            'r2_score_sous_famille': r2_score_sous_famille,
        })
    else:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
    

@require_GET
def get_metier_graph(request):
    code_uf = request.GET.get('code_uf')
    metier_graph_option = request.GET.get('metier_graph_option')
    rhs = RH.objects.filter(code_uf=code_uf)
    lits = Lit.objects.filter(code_uf=code_uf).order_by('semaine')
    df_rh = pd.DataFrame(list(rhs.values('semaine', 'metier', 'agents_abs_prevu', 'famille_metier', 'sous_famille_metier')))
    df_lits = pd.DataFrame(list(lits.values('semaine', 'lits_fermes_moyen')))
    if not df_lits.empty:
        df_lits['week_number'] = df_lits['semaine'].apply(lambda x: int(x.split(' - ')[0]) if x and ' - ' in str(x) else 0)
        df_lits['semaine'] = df_lits['week_number']
        df_lits.drop(columns=['week_number'], inplace=True)
    if code_uf and metier_graph_option:

        res_metier, graph_metier,_ = regression_call(df_rh,df_lits,'metier',code_uf, metier_graph_option)

        return JsonResponse({
            'graph_metier': graph_metier,
            'regression_res_metier': res_metier,  
        })
    elif code_uf:

        res_famille, graph_famille,__ = regression_call(df_rh,df_lits, 'famille_metier', code_uf, "famille")

        return JsonResponse({
            'graph_metier': graph_famille,
            'regression_res_famille': res_famille,
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
    coefs = {metier: round(float(model.coef_[i]),1) if model.coef_[i]>0 else 0 for i, metier in enumerate(metier_col_map.keys())}
    coefs['const'] = round(float(model.intercept_),1)
    r2_value = model.score(X, y)
    return coefs, r2_value


def figure_coeffs(data, title, mapping=None):
    
    
    plt.figure(figsize=(14,8))
    intercept = data.pop('const')
    features = list(data.keys())
    coefs = list(data.values())
    
    def generate_random_colors(n):
        """Generate n distinct random colors"""
        colors = []
        for i in range(n):
            # Use HSV color space to generate distinct colors
            hue = i / n
            saturation = 0.7 + random.random() * 0.3  # 0.7 to 1.0
            value = 0.6 + random.random() * 0.4       # 0.6 to 1.0
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255), 
                int(rgb[1] * 255), 
                int(rgb[2] * 255)
            )
            colors.append(hex_color)
        return colors
    
    if mapping:
        unique_categories = list(set(mapping.values()))
        category_colors = generate_random_colors(len(unique_categories))
        color_map = dict(zip(unique_categories, category_colors))
        
        colors = []
        for feature in features:
            category = mapping.get(feature, 'AUTRES')
            color = color_map.get(category, 'skyblue')
            colors.append(color)
        
        bars = plt.bar(features, coefs, color=colors)
        
        # Create legend with random colors
        legend_elements = []
        for category in unique_categories:
            color = color_map.get(category, 'skyblue')
            legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=color, label=category))
        plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 0.85))
    else:
        bars = plt.bar(features, coefs, color='skyblue')
    
    plt.axhline(0, color='gray', linewidth=0.8)

    plt.title("Effet de l'absence prévue sur fermeture de lits par "+title, fontsize=22)
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


def pivot_df(df, index_col, filter,value_col,df_lits):
        pivot = df.pivot_table(index=index_col, columns=filter, values=value_col, aggfunc='sum', fill_value=0).reset_index()
        df_merged = pd.merge(pivot, df_lits, on='semaine', how='left')
        return df_merged

def regression_call(df,df_lits,col,code_uf, metier_graph_option):
    df_merged= pivot_df(df, 'semaine', col, 'agents_abs_prevu',df_lits)
    cols= RH.objects.filter(code_uf=code_uf).values_list(col, flat=True).distinct()
    cols = [c for c in cols if c]
    res, r2_score= regression_lineaire(df_merged, cols)
    mapping = None
    if col == 'sous_famille_metier':
                # Map sous-famille to famille 
        mapping = {}
        sf_to_famille = RH.objects.filter(code_uf=code_uf).values('sous_famille_metier', 'famille_metier').distinct()
        for item in sf_to_famille:
            if item['sous_famille_metier'] and item['famille_metier']:
                mapping[item['sous_famille_metier']] = item['famille_metier']
    elif col == 'metier':
        mapping = {}
        if metier_graph_option == 'sous_famille':
            metier_to_sf = RH.objects.filter(code_uf=code_uf).values('metier', 'sous_famille_metier').distinct()
            for item in metier_to_sf:
                if item['metier'] and item['sous_famille_metier']:
                    mapping[item['metier']] = item['sous_famille_metier']
        else:
            metier_to_f= RH.objects.filter(code_uf=code_uf).values('metier', 'famille_metier').distinct()
            for item in metier_to_f:
                if item['metier'] and item['famille_metier']:
                    mapping[item['metier']] = item['famille_metier']
    graph = figure_coeffs(res.copy(), col.replace('_', ' ').title(), mapping)
    return res, graph, r2_score
        