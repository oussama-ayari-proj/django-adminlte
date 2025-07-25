from django.shortcuts import render

import sys
import os
import pickle
import pandas as pd
# Add the current app directory to Python path so MLflow can find custom_func
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from django.http import HttpResponse,JsonResponse
from apps.pages.models import UF
import mlflow
from datetime import datetime, timedelta

from apps.correlation.models import Lit
from apps.hospitalisation.models import Lits_occupes,Besoins
from sm1chut.predictions.pred import predict,mae_for_uf
from apps.hospitalisation.views import get_lits_fermes_kpis
from sklearn.metrics import mean_absolute_error as mae
import numpy as np

# Create your views here.

def index(request):
    ufs = UF.objects.order_by('libelle_standard')
    ufs_list = list(ufs.values('code_uf', 'libelle_standard'))
    
    # Get unique years from Besoins dates
    dates = Besoins.objects.dates('date', 'year', order='DESC')
    available_years = [date.year for date in dates]
    
    return render(request, 'predictions/index.html', {'ufs': ufs_list, 'years': available_years})

def get_predictions_stats(request):
    code_uf = request.GET.get('code_uf')
    year = request.GET.get('year')
    
    if not code_uf or not year:
        return JsonResponse({'error': 'Missing code_uf or year'}, status=400)
    
    try:
        # Get lits_installes for the UF
        lits_installes_obj = Lit.objects.filter(code_uf=code_uf).first()
        if not lits_installes_obj:
            lits_installes_value = 0
        else:
            lits_installes_value = lits_installes_obj.lits_installes

        besoin_lits = Besoins.objects.filter(
            code_uf=code_uf,
            date__year=year
        ).order_by('date').values('date', 'median')
        
        lits_occupes_total = Lits_occupes.objects.filter(
            code_uf=code_uf,
            date__year=year
        ).values('date', 'value')

        lits_occupes_list= []
        for item in lits_occupes_total:
            lits_occupes_list.append({
                'date': item['date'],
                'value': item['value']
            })
        lits_occupes_list.sort(key=lambda x: x['date'])

        besoin_lits_list= []
        for item in besoin_lits:
            besoin_lits_list.append({
                'date': item['date'],
                'median': item['median']
            })
        besoin_lits_list.sort(key=lambda x: x['date'])

        return JsonResponse({
            'besoin_lits': besoin_lits_list,
            'lits_occupes': lits_occupes_list,
            'lits_installes': lits_installes_value,
            'besoin_lits_kpis': get_lits_fermes_kpis(besoin_lits_list,'median'),
            'lits_occupes_kpis': get_lits_fermes_kpis(lits_occupes_list, 'value')
        })
        # Sort by week number
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_predictions(request):
    code_uf = request.GET.get('code_uf')
    end_date = request.GET.get('end_date')
    interval= request.GET.get('interval', 'false').lower() == 'true'
    latest_date = "2024-12-31"  # Default latest date
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    if isinstance(latest_date, str):
        latest_date = datetime.strptime(latest_date, '%Y-%m-%d').date()

    steps = (end_date - latest_date).days
    if steps<=0:
        return HttpResponse("Please provide the number of steps to predict.", status=400)

    # Get Besoin records from the last 3 months
    three_months_ago = datetime.strptime('2024-10-01', '%Y-%m-%d').date()
    besoin_records = None
    querySet = Besoins.objects.filter(
            code_uf=code_uf,
        )
    if code_uf:
        besoin_records = querySet.order_by('date').values('date', 'median')
        
        # Convert to list for JSON serialization
        besoin_list = []
        for item in besoin_records:
            besoin_list.append({
                'date': item['date'].strftime('%Y-%m-%d'),
                'median': item['median']
            })
    
    artifact_path = "pickle_folder/best_whole_data_1.pkl"
    run_id = "cd72dba36e884d908987606bf93ca28e"
    
    forecaster = load_model(artifact_path, run_id)
    artifact_path_mae = "pickle_folder/best_val_data_1.pkl"
    run_id_mae = "6f28a05c734241108f5409b094a5e05f"
    data_test_query= querySet.filter(
            date__gte=three_months_ago,
            date__lte=latest_date
        ).order_by('date').values('date', 'median','code_uf')
    data_test= pd.DataFrame.from_records(data_test_query)
    forecaster_mae = load_model(artifact_path_mae, run_id_mae)
    
    tab=predict(str(code_uf),forecaster,steps,interval=interval)
    formatted_dates = [date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date).split('T')[0] for date in tab.index]
    mae_dict=mae_for_uf(str(code_uf), forecaster_mae,data_test)
    res = {
        'date': formatted_dates,
        'value' : list(tab['pred']),
        'mae_months': list(mae_dict.keys()),
        'mae_values': list(round(val,2) for val in mae_dict.values())
    }
    
    
    if interval:
        res['upper_bound'] =list(tab['upper_bound'])
        res['lower_bound'] = list(tab['lower_bound'])
    return JsonResponse(res)
    
def load_model(artifact_path, run_id):
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("best_366")
    model_uri = f"runs:/{run_id}/{artifact_path}"

    local_path = mlflow.artifacts.download_artifacts(model_uri)

    # Load the model
    with open(local_path, "rb") as f:
        forecaster = pickle.load(f)
    
    return forecaster

def filter_ufs_with_mae_above_zero(request):
    """
    Optimized filter method that returns UFs with MAE > 0 between besoin and lits occupés
    """
    year = request.GET.get('year')
    
    if not year:
        return JsonResponse({'error': 'Missing year parameter'}, status=400)
    
    try:
        # Bulk fetch all data for the year in single queries
        besoin_data = Besoins.objects.filter(
            date__year=year
        ).values('code_uf', 'median').order_by('date')
        
        lits_occupes_data = Lits_occupes.objects.filter(
            date__year=year
        ).values('code_uf', 'value').order_by('date')
        
        # Group data by UF code for efficient lookup
        besoin_by_uf = {}
        lits_occupes_by_uf = {}
        
        for item in besoin_data:
            code_uf = item['code_uf']
            if code_uf not in besoin_by_uf:
                besoin_by_uf[code_uf] = []
            besoin_by_uf[code_uf].append(item['median'])
        
        for item in lits_occupes_data:
            code_uf = item['code_uf']
            if code_uf not in lits_occupes_by_uf:
                lits_occupes_by_uf[code_uf] = []
            lits_occupes_by_uf[code_uf].append(item['value'])
        
        # Get UF names in bulk
        uf_names = dict(UF.objects.values_list('code_uf', 'libelle_standard'))
        
        # Find UFs that have data in both datasets
        
        ufs_with_mae = []
        
        for code_uf in besoin_by_uf.keys():
            # Check if this UF also has lits_occupes data
            if code_uf not in lits_occupes_by_uf.keys():
                continue
                
            try:
                besoin_vals = besoin_by_uf[code_uf]
                lits_occupes_vals = lits_occupes_by_uf[code_uf]

                # Ensure both lists have data and same length
                min_length = min(len(besoin_vals), len(lits_occupes_vals))
                if min_length == 0:
                    continue

                # Check if any values are different
                has_difference = False
                for i in range(min_length):
                    if besoin_vals[i] != lits_occupes_vals[i]:
                        has_difference = True
                        break
                
                if has_difference:
                    ufs_with_mae.append({
                        'code_uf': code_uf,
                        'libelle_standard': uf_names.get(code_uf, f'UF {code_uf}'),
                    })
                    
            except Exception as e:
                print(f"Error calculating MAE for UF {code_uf}: {str(e)}")
                continue
        
        return JsonResponse({
            'ufs_with_mae': ufs_with_mae,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    