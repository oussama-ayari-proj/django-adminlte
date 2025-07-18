from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import Prediction
from apps.pages.models import UF
import mlflow
from apps.hospitalisation.models import Hospitalisation
from django.db.models import Max
from datetime import datetime
import holidays
from vacances_scolaires_france import SchoolHolidayDates
import pandas as pd
import sys
import os
import pickle

# Add the current app directory to Python path so MLflow can find custom_func
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from django.http import HttpResponse,JsonResponse
from .models import Prediction
from apps.pages.models import UF
import mlflow
from apps.hospitalisation.models import Hospitalisation
from django.db.models import Max
from datetime import datetime
import holidays
from vacances_scolaires_france import SchoolHolidayDates
import pandas as pd
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
    
    data_list = []
    for row in data:
        row = dict(row)
        if row['date']:
            row['date'] = row['date'].strftime('%Y-%m-%d')
        data_list.append(row)
    
    return JsonResponse(data_list, safe=False)

def get_predictions(request):
    code_uf = request.GET.get('code_uf')
    end_date = request.GET.get('end_date')
    latest_date = Hospitalisation.objects.aggregate(Max('date_sortie'))['date_sortie__max']
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    print(latest_date, end_date)
    years = set([end_date.year,latest_date.year])
    school_holidays = SchoolHolidayDates()
    dates_vacances = set()
    for year in years:
        vacances = school_holidays.holidays_for_year_and_zone(year, 'C')
        dates_vacances.update(vacances.keys())
    
    feries = holidays.France(years=years)

    steps = (end_date - latest_date).days
    if steps<=0:
        return HttpResponse("Please provide the number of steps to predict.", status=400)
    
    mlflow.set_tracking_uri("http://172.16.3.201:5000")
    mlflow.set_experiment("Exogs_FS_HT")
    artifact_path = "pickle_folder/best_1.pkl"
    run_id = "19d7fa6a856c488eb84af5d8e99de8ef"
    model_uri = f"runs:/{run_id}/{artifact_path}"

    local_path = mlflow.artifacts.download_artifacts(model_uri)

    # Load the model
    with open(local_path, "rb") as f:
        forecaster = pickle.load(f)


    date_range = pd.date_range(start=latest_date, end=end_date, freq='D')
    df= pd.DataFrame(columns=forecaster.exog_names_in_,index=date_range).fillna(0)
    df['vacances'] = df.index.isin(dates_vacances).astype(int)
    df['feries'] = df.index.isin(feries).astype(int)
    df['month'] = df.index.month
    df['day_of_week'] = df.index.dayofweek
    df['day_of_month'] = df.index.day
    df['week_of_year'] = df.index.isocalendar().week

    preds= forecaster.predict(steps=int(steps), levels=str(code_uf),exog=df)
    preds.reset_index(inplace=True)
    preds['pred'] = preds['pred'].apply(lambda x: round(x) if x>0 else 0)
    return JsonResponse({
        'predictions': list(preds['pred']),
        'dates': list(preds['index'].dt.strftime('%Y-%m-%d'))
    })

    