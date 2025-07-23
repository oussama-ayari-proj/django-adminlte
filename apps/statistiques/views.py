from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

from apps.hebergement_hors_uf.models import EM,Matrice_EM_UF,export_UF
from apps.hospitalisation.models import Hospitalisation
from apps.pages.models import UF, Pole
from .models import ChargeEM



@login_required
def statistiques_globales(request):
    # Get available years from hospitalisation data
    years = Hospitalisation.objects.dates('date_entree', 'year', order='DESC')
    available_years = [year.year for year in years]
    
    context = {
        'available_years': available_years
    }
    return render(request, 'statistiques/statistiques_globales.html', context)

@require_GET
def api_global_stats(request):
    year = request.GET.get('year')
    if year:
        total_ems = EM.objects.count()
        total_sejours = Hospitalisation.objects.filter(date_entree__year=year).count()
        valid_pairs = set(Matrice_EM_UF.objects.values_list('code_em', 'code_uf'))
        hebergements = Hospitalisation.objects.filter(date_entree__year=year).exclude(code_uf__isnull=True)
        total_hebergements = 0
        for h in hebergements.values('code_em', 'code_uf'):
            if (h['code_em'], h['code_uf']) not in valid_pairs:
                total_hebergements += 1
        return JsonResponse({
            'total_ems': total_ems,
            'total_sejours': total_sejours,
            'total_hebergements': total_hebergements
        })
    else:
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
def api_ems_by_year(request):
    year = request.GET.get('year')
    if not year:
        return JsonResponse({'error': 'Year parameter is required'}, status=400)
    
    # Get all UFs associées for all EMs in one query
    ufs_associees_by_em = {}
    for matrice in Matrice_EM_UF.objects.all():
        if matrice.code_em not in ufs_associees_by_em:
            ufs_associees_by_em[matrice.code_em] = set()
        ufs_associees_by_em[matrice.code_em].add(matrice.code_uf)
    
    # Get EMs with interventions and their UFs in one optimized query
    em_uf_data = (Hospitalisation.objects
                 .filter(date_entree__year=year)
                 .values('code_em', 'code_uf')
                 .distinct())
    
    # Group UFs by EM
    ufs_by_em = {}
    for item in em_uf_data:
        code_em = item['code_em']
        code_uf = item['code_uf']
        if code_em not in ufs_by_em:
            ufs_by_em[code_em] = set()
        ufs_by_em[code_em].add(code_uf)
    
    # Get all EMs for the year
    ems_with_interventions = list(ufs_by_em.keys())
    
    # Get EM details in one query
    ems_details = {em.code_em: em.libelle_em for em in EM.objects.filter(code_em__in=ems_with_interventions)}
    
    # Build final result
    ems_with_data = [
        {
            'code_em': code_em,
            'libelle_em': ems_details.get(code_em, f'EM {code_em}')
        }
        for code_em in ems_with_interventions
        if code_em in ems_details
    ]
    
    return JsonResponse({
        'ems': ems_with_data,
        'count': len(ems_with_data)
    }, status=200)

@require_GET
def api_em_stats(request):
    code_em = request.GET.get('code_em')
    year = request.GET.get('year')
    if not code_em:
        return JsonResponse({'error': 'Missing code_em'}, status=400)
    
    # Filter by year if provided
    if year:
        sejours = Hospitalisation.objects.filter(code_em=code_em, date_entree__year=year).count()
        hebergements = Hospitalisation.objects.filter(code_em=code_em, date_entree__year=year).exclude(code_uf__isnull=True)
    else:
        sejours = Hospitalisation.objects.filter(code_em=code_em).count()
        hebergements = Hospitalisation.objects.filter(code_em=code_em).exclude(code_uf__isnull=True)
    
    # Get all code_uf for this code_em in Matrice_EM_UF
    valid_ufs = set(Matrice_EM_UF.objects.filter(code_em=code_em).values_list('code_uf', flat=True))
    hebergement_count = 0
    for h in hebergements.values_list('code_uf', flat=True):
        if h not in valid_ufs:
            hebergement_count += 1
    
    # Get UF names for associated UFs
    uf_names = []
    if valid_ufs:
        ufs = UF.objects.filter(code_uf__in=valid_ufs).values('code_uf', 'libelle_standard')
        uf_names = [
            {
                'code_uf': uf['code_uf'],
                'libelle_uf': uf['libelle_standard'].strip() if uf['libelle_standard'] else f"UF {uf['code_uf']}"
            }
            for uf in ufs
        ]
    
    # Get pole information from Matrice_EM_UF
    pole_info = None
    try:
        matrice_entry = Matrice_EM_UF.objects.filter(code_em=code_em).first()
        if matrice_entry and matrice_entry.code_pole:
            try:
                pole = Pole.objects.get(code_pole=matrice_entry.code_pole)
                pole_info = {
                    'code_pole': pole.code_pole,
                    'libelle_pole': pole.libelle_standard.strip() if pole.libelle_standard else f"Pole {pole.code_pole}"
                }
            except Pole.DoesNotExist:
                pole_info = {
                    'code_pole': matrice_entry.code_pole,
                    'libelle_pole': f"Pole {matrice_entry.code_pole}"
                }
    except Exception:
        pole_info = None
    
    return JsonResponse({
        'sejours': sejours,
        'hebergements': hebergement_count,
        'uf_associees': uf_names,
        'pole': pole_info
    })

@require_GET
def get_charge_em(request):
    code_em = request.GET.get('code_em')
    year = request.GET.get('year')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not code_em:
        return JsonResponse({'error': 'Missing code_em'}, status=400)

    # Start with base filter
    queryset = ChargeEM.objects.filter(code_em=code_em)
    
    # Apply date filters
    if year:
        queryset = queryset.filter(date__year=year)
    
    if start_date:
        queryset = queryset.filter(date__gte=start_date)
        
    if end_date:
        queryset = queryset.filter(date__lte=end_date)
    
    # Order by date and get values
    data = queryset.order_by('date').values('date', 'charge','code_uf')
    
    # Get all UF codes and their labels in one query for efficiency
    uf_codes = set(row['code_uf'] for row in data if row['code_uf'])
    uf_labels = {uf.code_uf: uf.libelle_standard for uf in export_UF.objects.filter(code_uf__in=uf_codes)}
    
    result = [
        {
            'date': row['date'].strftime('%Y-%m-%d') if row['date'] else str(row['date']),
            'charge_em': row['charge'],
            'libelle_uf': uf_labels.get(row.get('code_uf')) if row.get('code_uf') else None
        }
        for row in data
    ]
    return JsonResponse(result, safe=False)
    
    
