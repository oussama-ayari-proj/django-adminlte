from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.db.models import Count, Avg
from django.views.decorators.csrf import csrf_exempt
from .models import EM,Matrice_EM_UF,export_UF
from apps.hospitalisation.models import Hospitalisation
from apps.pages.models import UF
from apps.correlation.models import Lit
import numpy as np

def index(request):
    # Get available years from hospitalisation data
    years = Hospitalisation.objects.dates('date_entree', 'year', order='DESC')
    available_years = [year.year for year in years]
    
    return render(request, 'hebergement_hors_uf/index.html', {
        'available_years': available_years
    })

def calculer_lits_fermes(code_uf_associe,year):
    lits_fermes_by_week = {}
    lits_fermes_data = []
    if isinstance(code_uf_associe, str):
        code_uf_associe = [code_uf_associe]
    
    
    if len(code_uf_associe)==1:
        lits= Lit.objects.filter(
            code_uf=code_uf_associe[0],
            semaine__endswith=f" - {year}"
        )
        if not lits.exists():
            return []
        for lit in lits:
            semaine = lit.semaine.split(' - ')[0]
            print(type(semaine))
            lits_fermes_moyen = lit.lits_fermes_moyen or 0
            lits_fermes_data.append({
                'semaine': semaine,
                'lits_fermes_moyen': round(lits_fermes_moyen, 1),
            })
            
        return lits_fermes_data
    for code_uf in code_uf_associe:
        lits= Lit.objects.filter(
            code_uf=code_uf,
            semaine__endswith=f" - {year}"
        )
        for lit in lits:
            semaine = lit.semaine.split(' - ')[0]
            lits_fermes_moyen = lit.lits_fermes_moyen or 0

            if semaine not in lits_fermes_by_week:
                lits_fermes_by_week[semaine] = []
                continue         
            lits_fermes_by_week[semaine].append(lits_fermes_moyen)
                
    for semaine, lits_list in lits_fermes_by_week.items():
        if len(lits_list) > 0:
            moyenne_lits_fermes = sum(lits_list)
            lits_fermes_data.append({
                'semaine': semaine,
                'lits_fermes_moyen': round(moyenne_lits_fermes, 1)
            })
    return lits_fermes_data

def get_hebergement_stats(request):
    code_em = request.GET.get('code_em')
    year = request.GET.get('year')
    
    if not code_em or not year:
        return JsonResponse({'error': 'Code EM and Year are required'}, status=400)
    
    try:
        # Single optimized query for all interventions
        total_interventions = Hospitalisation.objects.filter(
            code_em=code_em, 
            date_entree__year=year
        )
        
        stats = {}
        stats['total_interventions'] = total_interventions.count()
        
        # Get UFs associées
        code_uf_associees = list(Matrice_EM_UF.objects.filter(code_em=code_em).values_list('code_uf', flat=True))
        
        # Get hébergements (interventions outside UFs associées)
        hebergements_data = total_interventions.exclude(code_uf__in=code_uf_associees)
        stats['total_hebergement'] = hebergements_data.count()
        
        # Get UF associées details
        uf_associees = export_UF.objects.filter(code_uf__in=code_uf_associees).values('code_uf', 'libelle_standard')
        
        # Filter UFs associées to only include those with lits_fermes > 0
        year_int = int(year)
        ufs_with_lits_fermes = []
        for uf in uf_associees:
            # Check if this UF has any lits_fermes > 0 for the given year
            lits_count = Lit.objects.filter(
                code_uf=uf['code_uf'],
                semaine__endswith=f" - {year_int}",
                lits_fermes_moyen__gt=0
            ).count()
            
            if lits_count > 0:
                ufs_with_lits_fermes.append(uf)
        
        # Group hébergements efficiently
        hebergements_grouped = hebergements_data.values('semaine_entree', 'code_uf', 'ghs', 'type_sejour').annotate(
            nombre_hospitalisations=Count('id')
        ).order_by('semaine_entree', 'code_uf')
        
        # Get UF labels in one query
        uf_codes = set(h['code_uf'] for h in hebergements_grouped)
        uf_labels = {uf.code_uf: uf.libelle_standard for uf in export_UF.objects.filter(code_uf__in=uf_codes)}
        
        # Build hébergements with labels
        hebergements_with_labels = []
        for hebergement in hebergements_grouped:
            hebergement_dict = dict(hebergement)
            hebergement_dict['libelle_uf'] = uf_labels.get(hebergement['code_uf'], str(hebergement['code_uf']))
            hebergements_with_labels.append(hebergement_dict)
        
        stats['hebergements'] = hebergements_with_labels
        
        
        
        return JsonResponse({
            'stats': stats,
            'uf_associees': ufs_with_lits_fermes
        }, status=200)
        
    except Exception as e:
        print(f"Error in get_hebergement_stats: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
def get_lits_fermes_filtres(request):
    code_uf_associe = request.GET.get('code_uf_associe')
    year = request.GET.get('year')
    if not code_uf_associe:
        return JsonResponse({'error': 'Aucun code UF associé fourni'}, status=400)
    try:
        if ',' in code_uf_associe:
            code_uf_associe = code_uf_associe.split(',')
        lits_fermes_data = calculer_lits_fermes(code_uf_associe,year)
        return JsonResponse({
            'lits_fermes': lits_fermes_data
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_ems_by_year(request):
    year = request.GET.get('year')
    print('Year:', year)
    if not year:
        return JsonResponse({'error': 'Year parameter is required'}, status=400)
    
    try:
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
                     .annotate(count=Count('id'))
                     .filter(count__gt=0))
        
        # Group UFs by EM
        ufs_by_em = {}
        for item in em_uf_data:
            code_em = item['code_em']
            code_uf = item['code_uf']
            if code_em not in ufs_by_em:
                ufs_by_em[code_em] = set()
            ufs_by_em[code_em].add(code_uf)
        
        # Find EMs with hébergements (UFs not in their associated UFs)
        ems_with_hebergements_codes = []
        for code_em, ufs in ufs_by_em.items():
            ufs_associees = ufs_associees_by_em.get(code_em, set())
            if ufs - ufs_associees:  # If there are UFs not in associated UFs
                ems_with_hebergements_codes.append(code_em)
        
        # Get EM details in one query
        ems_details = {em.code_em: em.libelle_em for em in EM.objects.filter(code_em__in=ems_with_hebergements_codes)}
        
        # Build final result
        ems_with_hebergements = [
            {
                'code_em': code_em,
                'libelle_em': ems_details.get(code_em, f'EM {code_em}')
            }
            for code_em in ems_with_hebergements_codes
            if code_em in ems_details
        ]
        
        
        return JsonResponse({
            'ems': ems_with_hebergements,
            'count': len(ems_with_hebergements)
        }, status=200)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def calculate_hebergement_stats(code_em):
    total_interventions = Hospitalisation.objects.filter(code_em=code_em)
    total_interventions_count = total_interventions.count()
    ufs_associees = Matrice_EM_UF.objects.filter(code_em=code_em).values_list('code_uf', flat=True)
    hebergements= total_interventions.exclude(code_uf__in=ufs_associees)
    total_hebergements_count = hebergements.count()

    return total_interventions_count,total_hebergements_count,hebergements

