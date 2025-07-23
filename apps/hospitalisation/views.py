from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Min, Max, Avg, Count
from django.core.paginator import Paginator
from apps.hospitalisation.models import Hospitalisation,Lits_occupes
from apps.pages.models import UF, ETB, Pole
from apps.correlation.models import Lit, RH
from apps.hebergement_hors_uf.models import Matrice_EM_UF,EM
from django.db import models
import numpy as np


def index(request):
    ufs = UF.objects.order_by('libelle_standard')
    ufs_list = list(ufs.values('code_uf', 'libelle_standard'))
    return render(request, 'hospitalisation/index.html',{'ufs': ufs_list})

    
def get_hospitalisation_stats(request):
    code_uf = request.GET.get('code_uf')
    stats={}
    # Add ETB, Pôle, and Lits installés data
    if code_uf:
        try:
            # Get ETB info
            uf = UF.objects.get(code_uf=code_uf)
            stats['type_activite'] = uf.libelle_type_activite.strip() if uf.libelle_type_activite else 'Non spécifié'
            em_associes = Matrice_EM_UF.objects.filter(code_uf=code_uf).values_list('code_em', flat=True)
            em_associes_libelle = EM.objects.filter(code_em__in=em_associes).values_list('libelle_em', flat=True)
            stats['em_associes'] = [
                em.strip() if em else 'Non spécifié' for em in em_associes_libelle
            ]
            
            
            try:
                etb = ETB.objects.get(code_etb=uf.code_etb)
                stats['etb'] = etb.libelle_standard.strip() if etb.libelle_standard else 'Non spécifié'
            except ETB.DoesNotExist:
                stats['etb'] = 'Non spécifié'
            
            # Get Pôle info
            try:
                pole = Pole.objects.get(code_pole=uf.code_pole)
                stats['pole'] = pole.libelle_standard.strip() if pole.libelle_standard else 'Non spécifié'
            except Pole.DoesNotExist:
                stats['pole'] = 'Non spécifié'
            
            # Get Lits installés moyens
            try:
                lits = Lit.objects.filter(code_uf=code_uf)
                if lits.exists():
                    avg_lits = lits.aggregate(avg_lits=Avg('lits_installes'))['avg_lits']
                    stats['lits_installes'] = round(avg_lits, 1) if avg_lits else 0
                else:
                    stats['lits_installes'] = 0
            except Exception:
                stats['lits_installes'] = 0
                  # Get Métiers data
            try:
                metiers_data = RH.objects.filter(code_uf=code_uf).values('metier').annotate(
                    total_effectif=Avg('effectif_total')
                ).filter(metier__isnull=False).order_by('-total_effectif')
                
                metiers_list = [
                    {
                        'metier': item['metier'].strip() if item['metier'] else 'Non spécifié',
                        'effectif': round(item['total_effectif']) if item['total_effectif'] else 0
                    }
                    for item in metiers_data
                ]
                
                # Calculate total effectif
                total_effectif = sum(metier['effectif'] for metier in metiers_list)
                
                stats['metiers'] = metiers_list
                stats['metiers_total'] = total_effectif
            except Exception:
                stats['metiers'] = []
                stats['metiers_total'] = 0
                
        except UF.DoesNotExist:
            stats['etb'] = 'Non spécifié'
            stats['pole'] = 'Non spécifié'
            stats['lits_installes'] = 0
            stats['metiers'] = []
            stats['metiers_total'] = 0
    else:
        stats['etb'] = 'Non spécifié'
        stats['pole'] = 'Non spécifié'
        stats['lits_installes'] = 0
        stats['metiers'] = []
        stats['metiers_total'] = 0
    
    return JsonResponse(stats)


@require_GET
def get_hospitalisation_data(request):
    try:
        queryset = Hospitalisation.objects.all()
        
        # Apply filters
        code_uf = request.GET.get('code_uf')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if code_uf:
            queryset = queryset.filter(code_uf=code_uf)
        if start_date:
            queryset = queryset.filter(date_entree__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_entree__lte=end_date)
        
        # Order by date
        queryset = queryset.order_by('-date_entree')
        
        # Pagination
        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 100)
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        # Convert to list of dictionaries
        data = []
        for item in page_obj:            
            data.append({
                'numero_sejour': item.num_sequence,
                'date_entree': item.date_entree.strftime('%Y-%m-%d') if item.date_entree else None,
                'date_sortie': item.date_sortie.strftime('%Y-%m-%d') if item.date_sortie else None,
                'duree_sejour': item.duree_sejour,
                'code_uf': item.code_uf,
                'type_sejour': item.type_sejour,
                'mode_sortie': item.ghs,  # Using GHS as mode_sortie placeholder
            })
        
        return JsonResponse({
            'data': data,
            'total': paginator.count,
            'page': page_obj.number,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def get_date_ranges(request):
    try:
        date_ranges = Hospitalisation.objects.aggregate(
            min_date_entree=Min('date_entree'),
            max_date_entree=Max('date_entree'),
            min_date_sortie=Min('date_sortie'),
            max_date_sortie=Max('date_sortie')
        )
        
        # Convert dates to strings for JSON serialization
        return JsonResponse({
            'min_date': str(date_ranges['min_date_entree']) if date_ranges['min_date_entree'] else None,
            'max_date': str(date_ranges['max_date_sortie']) if date_ranges['max_date_sortie'] else None,
            'min_entree': str(date_ranges['min_date_entree']) if date_ranges['min_date_entree'] else None,
            'max_entree': str(date_ranges['max_date_entree']) if date_ranges['max_date_entree'] else None,
            'min_sortie': str(date_ranges['min_date_sortie']) if date_ranges['min_date_sortie'] else None,
            'max_sortie': str(date_ranges['max_date_sortie']) if date_ranges['max_date_sortie'] else None
        })
    except Exception as e:
        print(f"Error in get_date_ranges: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def analyse_sejours(request):
    """View for the Analyse des Séjours page"""
    ufs = UF.objects.order_by('libelle_standard')
    ufs_list = list(ufs.values('code_uf', 'libelle_standard'))
    return render(request, 'hospitalisation/analyse_sejours.html', {'ufs': ufs_list})


@require_GET
def get_sejours_analysis(request):
    """API endpoint for séjours analysis data"""
    try:
        code_uf = request.GET.get('code_uf')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Base queryset
        queryset = Hospitalisation.objects.all()
        
        # Apply filters
        if code_uf:
            queryset = queryset.filter(code_uf=code_uf)
        if start_date:
            queryset = queryset.filter(date_entree__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_entree__lte=end_date)

        # Get statistics
        stats = queryset.aggregate(
            total_sejours=Count('id'),
            duree_moyenne=Avg('duree_sejour'),
            patients_uniques=Count('num_sequence', filter=models.Q(num_sequence=1)),
        )
        
        # Get type séjours distribution for histogram
        type_sejours = list(queryset.values('type_sejour').annotate(
            count=Count('id')
        ).filter(type_sejour__isnull=False).order_by('-count'))
        
        
        hebergement_count,heb_data = calculer_hebergements(code_uf, queryset)
        total_count = queryset.count()
        pourcentage_hebergement = (hebergement_count / total_count * 100) if total_count > 0 else 0
        
        # Round values for display
        stats['duree_moyenne'] = round(stats['duree_moyenne'], 1) if stats['duree_moyenne'] else 0
        stats['total_sejours'] = stats['total_sejours'] or 0
        stats['patients_uniques'] = stats['patients_uniques'] or 0
        
        return JsonResponse({
            'total_sejours': stats['total_sejours'],
            'duree_moyenne': stats['duree_moyenne'],
            'patients_uniques': stats['patients_uniques'],
            'type_sejours': type_sejours,
            'nombre_hebergement': hebergement_count,
            'pourcentage_hebergement': round(pourcentage_hebergement, 1),
            'charge': list(queryset.values(
                'date_entree'
            ).annotate(
                count=Count('id')
            ).order_by('date_entree')),
            'hebergement_data': list(heb_data),
        })
        
    except Exception as e:
        print(f"Error in get_sejours_analysis: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
def calculer_hebergements(code_uf,data):
    try:
        em_associes = Matrice_EM_UF.objects.filter(code_uf=code_uf).values_list('code_em', flat=True)
        heb_data_raw = data.exclude(code_em__in=em_associes).values_list(
            'date_entree', 'code_em'
        )
        
        # Create a mapping of code_em to libelle_em
        em_codes = set(item[1] for item in heb_data_raw if item[1])  # Get unique EM codes
        em_mapping = {}
        for em_code in em_codes:
            try:
                em = EM.objects.get(code_em=em_code)
                em_mapping[em_code] = em.libelle_em.strip() if em.libelle_em else f"EM_{em_code}"
            except EM.DoesNotExist:
                em_mapping[em_code] = f"EM_{em_code}"
        
        # Replace code_em with libelle_em in the data
        heb_data = []
        for date_entree, code_em in heb_data_raw:
            em_label = em_mapping.get(code_em, f"EM_{code_em}")
            heb_data.append([
                date_entree,
                em_label
            ])
        heb_count = len(heb_data)
        return heb_count, heb_data
    except Exception as e:
        print(f"Error in calculer_hebergements: {e}")
        return 0, []

def index_lits_fermes(request):
    """View for the Lits Fermés page"""
    ufs = UF.objects.order_by('libelle_standard')
    ufs_list = list(ufs.values('code_uf', 'libelle_standard'))
    available_years=[2023, 2024]
    return render(request, 'hospitalisation/lits_fermes.html', {
        'ufs': ufs_list, 
        'available_years': available_years
    })

def get_lits_fermes_stats(request):
    code_uf = request.GET.get('code_uf')
    year = request.GET.get('year')
    
    if not code_uf or not year:
        return JsonResponse({'error': 'Missing code_uf or year'}, status=400)
    
    try:

        lits_data = Lit.objects.filter(
            code_uf=code_uf,
            semaine__endswith=f" - {year}"
        )
        
        lits_occupes_total = Lits_occupes.objects.filter(
            code_uf=code_uf,
            date__year=year
        ).values('date', 'value')

        lits_list = []
        for lit in lits_data:
            try:
                week_number = int(lit.semaine.split(' - ')[0])
            except (ValueError, IndexError):
                week_number = 0 
            
            lits_list.append({
                'semaine': lit.semaine,
                'week_number': week_number,
                'lits_installes': lit.lits_installes,
                'lits_fermes': lit.lits_fermes_moyen,
                'code_uf': lit.code_uf
            })
        
        lits_occupes_list= []
        for item in lits_occupes_total:
            lits_occupes_list.append({
                'date': item['date'],
                'lits_occupes': item['value']
            })
        lits_occupes_list.sort(key=lambda x: x['date'])
        # Sort by week number
        lits_list.sort(key=lambda x: x['week_number'])

        stats_lits= get_lits_fermes_kpis(lits_list, 'lits_fermes', 'lits_installes')
        stats_lits['lits_data'] = lits_list

        stats_lits_occupes = get_lits_fermes_kpis(lits_occupes_list, 'lits_occupes')
        stats_lits_occupes['lits_occupes_data'] = list(lits_occupes_total) if lits_occupes_total else []
        # Calculate summary statistics
        
        stats_lits_occupes.update(stats_lits)
        
        return JsonResponse(stats_lits_occupes,safe=False)
        
    except Exception as e:
        print(f"Error in get_lits_fermes_stats: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def get_lits_fermes_kpis(data,col,col2=None):
    target = [float(item[col]) if item[col] else 0 for item in data]

    total_records = len(data)
    if col2:
        avg_lits_installes = sum(float(item[col2]) for item in data if item[col2]) / total_records if total_records > 0 else 0
    avg_target = np.mean(target)
    min_target = min((target), default=0)
    max_target = max((target), default=0)
    var_target=np.var(target) if total_records > 0 else 0
    std_target = np.std(target) if total_records > 0 else 0

    stats = {
        f'mean_{col}': round(avg_target, 1),
        f'min_{col}': round(min_target,1),
        f'max_{col}': round(max_target,1),
        f'std_{col}': round(std_target, 1) if std_target else 0,
        f'var_{col}': round(var_target, 1) if var_target else 0,
    }
    if col2:
        stats['lits_installes'] = round(avg_lits_installes, 1)
    return stats