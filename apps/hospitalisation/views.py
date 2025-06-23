from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Min, Max, Avg, Count
from django.core.paginator import Paginator
from apps.hospitalisation.models import Hospitalisation,Lits_occupes
from apps.pages.models import UF, ETB, Pole
from apps.correlation.models import Lit, RH


def index(request):
    ufs = UF.objects.order_by('libelle_standard')
    ufs_list = list(ufs.values('code_uf', 'libelle_standard'))
    return render(request, 'hospitalisation/index.html',{'ufs': ufs_list})

    
def get_hospitalisation_stats(request):
    code_uf = request.GET.get('code_uf')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    stats = Hospitalisation.get_stats(code_uf, start_date, end_date)
    
    # Add ETB, Pôle, and Lits installés data
    if code_uf:
        try:
            # Get ETB info
            uf = UF.objects.get(code_uf=code_uf)
            lits_occupes = Lits_occupes.objects.filter(code_uf=code_uf).order_by('date')
            if lits_occupes.exists():
                stats['lits_occupes'] = list(lits_occupes.values('date','lits_occupes'))
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
                'age_patient': item.age_entree,
                'sexe_patient': item.sexe_display
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
        return JsonResponse({'error': str(e)}, status=500)
