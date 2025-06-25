from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.db.models import Count, Avg
from django.views.decorators.csrf import csrf_exempt
import json
from .models import EM,Matrice_EM_UF,export_UF
from apps.hospitalisation.models import Hospitalisation
from apps.pages.models import UF
from apps.correlation.models import Lit

def index(request):

    ems = EM.objects.order_by('libelle_em')
    ems_list = list(ems.values('code_em', 'libelle_em'))
    
    stats = {}
    stats['total_equipes'] = ems.count()
    stats['total_interventions_globales'] = Hospitalisation.objects.count()
    
    total_hebergements_globaux = 0
    for em in ems:
        _, hebergements_em, hebergements_data = calculate_hebergement_stats(em.code_em)
        total_hebergements_globaux += hebergements_em
    
    stats['total_hebergements_globaux'] = total_hebergements_globaux
    return render(request, 'hebergement_hors_uf/index.html', {
        'ems': ems_list,
        'total_equipes': stats['total_equipes'],
        'total_interventions_globales': stats['total_interventions_globales'],
        'total_hebergements_globaux': stats['total_hebergements_globaux'],
    })

def calculer_lits_fermes(code_uf_associe):
    lits_fermes_by_week = {}
    lits_fermes_data = []
    if isinstance(code_uf_associe, str):
        code_uf_associe = [code_uf_associe]
    if len(code_uf_associe)==1:
        lits= Lit.objects.filter(code_uf=code_uf_associe[0])
        if not lits.exists():
            return []
        for lit in lits:
            semaine = lit.semaine
            lits_fermes_moyen = lit.lits_fermes_moyen or 0
            lits_fermes_data.append({
                'semaine': semaine,
                'lits_fermes_moyen': round(lits_fermes_moyen, 1)
            })
            
        return lits_fermes_data
    for code_uf in code_uf_associe:
        lits = Lit.objects.filter(code_uf=code_uf)
        for lit in lits:
            semaine = lit.semaine
            lits_fermes_moyen = lit.lits_fermes_moyen or 0

            if semaine not in lits_fermes_by_week:
                lits_fermes_by_week[semaine] = []
                continue         
            lits_fermes_by_week[semaine].append(lits_fermes_moyen)
                
    for semaine, lits_list in lits_fermes_by_week.items():
        if len(lits_list) > 0:
            moyenne_lits_fermes = sum(lits_list) / len(lits_list)
            lits_fermes_data.append({
                'semaine': semaine,
                'lits_fermes_moyen': round(moyenne_lits_fermes, 1)
            })
    return lits_fermes_data

def get_hebergement_stats(request):
    code_em = request.GET.get('code_em')
    stats = {}
    if code_em:
        try:
            stats['total_interventions'], stats['total_hebergement'], hebergements_data = calculate_hebergement_stats(code_em)
            code_uf_associees = Matrice_EM_UF.objects.filter(code_em=code_em).values_list('code_uf', flat=True)
            uf_associees = export_UF.objects.filter(code_uf__in=code_uf_associees).values('code_uf', 'libelle_standard')
            
            hebergements_grouped = hebergements_data.values('semaine_entree', 'code_uf', 'ghs', 'type_sejour').annotate(
                nombre_hospitalisations=Count('id')
            ).order_by('semaine_entree', 'code_uf')
            
            hebergements_with_labels = []
            
            for hebergement in hebergements_grouped:
                uf_hebergement = export_UF.objects.filter(code_uf=hebergement['code_uf']).first()
                hebergement_dict = dict(hebergement)
                hebergement_dict['libelle_uf'] = uf_hebergement.libelle_standard if uf_hebergement else hebergement['code_uf']
                hebergements_with_labels.append(hebergement_dict)
            
            stats['hebergements'] = hebergements_with_labels
            
            # Ajouter les données de lits fermés pour les UFs associées
            lits_fermes_data = []
            if code_uf_associees:
                lits_fermes_data = calculer_lits_fermes(code_uf_associees)

            stats['lits_fermes'] = lits_fermes_data
            
        except EM.DoesNotExist:
            return JsonResponse({
                'error': 'EM not found',
            }, status=404)

    return JsonResponse({
        'stats': stats,
        'uf_associees': list(uf_associees)
    }, status=200)

def get_lits_fermes_filtres(request):
    code_uf_associe = request.GET.get('code_uf_associe')
    if not code_uf_associe:
        return JsonResponse({'error': 'Aucun code UF associé fourni'}, status=400)
    try:
        if ',' in code_uf_associe:
            code_uf_associe = code_uf_associe.split(',')
        lits_fermes_data = calculer_lits_fermes(code_uf_associe)
        return JsonResponse({
            'lits_fermes': lits_fermes_data
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_ems_with_hebergements(request):
    try:
        ems_with_hebergements = []
        
        # Parcourir toutes les équipes et vérifier lesquelles ont des hébergements
        for em in EM.objects.all():
            _, total_hebergements,__ = calculate_hebergement_stats(em.code_em)
            if total_hebergements > 0:
                ems_with_hebergements.append({
                    'code_em': em.code_em,
                    'libelle_em': em.libelle_em
                })
        
        return JsonResponse({
            'ems': ems_with_hebergements,
            'count': len(ems_with_hebergements)
        }, status=200)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def calculate_hebergement_stats(code_em):
    total_interventions = Hospitalisation.objects.filter(code_em=code_em)
    total_interventions_count = total_interventions.count()
    ufs_associees = Matrice_EM_UF.objects.filter(code_em=code_em).values_list('code_uf', flat=True)
    hebergements= total_interventions.exclude(code_uf__in=ufs_associees)
    total_hebergements_count = hebergements.count()

    return total_interventions_count,total_hebergements_count,hebergements
    


