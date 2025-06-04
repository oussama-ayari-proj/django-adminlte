from django.shortcuts import render
from django.core.paginator import Paginator
from .models import UF, Sejour, EM
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET

def index(request):
    ufs = UF.objects.all()
    sejours = Sejour.objects.all()
    ems = EM.objects.all()

    # Pagination for UF
    paginator_ufs = Paginator(ufs, 5)
    page_number_uf = request.GET.get('page_uf')
    ufs_page = paginator_ufs.get_page(page_number_uf)

    # Pagination for Sejours
    paginator_sejours = Paginator(sejours, 10)
    page_number_sejour = request.GET.get('page_sejour')
    sejours_page = paginator_sejours.get_page(page_number_sejour)

    # Pagination for EM
    paginator_ems = Paginator(ems, 7)
    page_number_em = request.GET.get('page_em')
    ems_page = paginator_ems.get_page(page_number_em)

    return render(request, 'pages/index.html', {
        'ufs': ufs_page,
        'sejours': sejours_page,
        'ems': ems_page
    })

def ajax_ufs_pagination(request):
    ufs = UF.objects.all()
    paginator_ufs = Paginator(ufs, 5)
    page_number_uf = request.GET.get('page_uf')
    ufs_page = paginator_ufs.get_page(page_number_uf)
    table_html = render_to_string('pages/partials/uf_table_body.html', {'ufs': ufs_page})
    pagination_html = render_to_string('pages/partials/uf_pagination.html', {'ufs': ufs_page})
    return JsonResponse({'table_body': table_html, 'pagination': pagination_html})

def ajax_sejours_pagination(request):
    sejours = Sejour.objects.all()
    paginator_sejours = Paginator(sejours, 10)
    page_number_sejour = request.GET.get('page_sejour')
    sejours_page = paginator_sejours.get_page(page_number_sejour)
    table_html = render_to_string('pages/partials/sejour_table_body.html', {'sejours': sejours_page})
    pagination_html = render_to_string('pages/partials/sejour_pagination.html', {'sejours': sejours_page})
    return JsonResponse({'table_body': table_html, 'pagination': pagination_html})

def ajax_em_pagination(request):
    em = EM.objects.all()
    paginator_em = Paginator(em, 5)
    page_number_em = request.GET.get('page_em')
    field = request.GET.get('field')
    value= request.GET.get('value')
    print(f"Field: {field}, Value: {value}")
    if not field or not value:
        field = None
    if field and value:
        em = em.filter(**{field: value})
        paginator_em = Paginator(em, 5)
    ems_page = paginator_em.get_page(page_number_em)
    table_html = render_to_string('pages/partials/em_table_body.html', {'ems': ems_page})
    pagination_html = render_to_string('pages/partials/em_pagination.html', {'ems': ems_page})
    return JsonResponse({'table_body': table_html, 'pagination': pagination_html})

@require_GET
def ajax_uf_unique_values(request):
    field = request.GET.get('field')
    allowed_fields = [
        'libelle_standard', 'code_uf', 'code_etb', 'code_pole', 'heb',
        'type_uf', 'libelle_type_uf', 'type_activite', 'libelle_type_activite'
    ]
    values = []
    if field in allowed_fields:
        values = list(
            UF.objects
            .values_list(field, flat=True)
            .distinct()
        )
        values = [str(v) for v in values if v not in [None, '']]
    return JsonResponse({'values': values})


@require_GET
def ajax_sejour_unique_values(request):
    field = request.GET.get('field')
    allowed_fields = [
        'num_sequence', 'code_uf', 'code_em', 'duree_sejour', 'type_sejour',
        'date_sortie', 'ghs', 'sexe', 'age_entree', 'semaine_entree', 'date_entree'
    ]
    values = []
    if field in allowed_fields:
        values = list(
            Sejour.objects
            .values_list(field, flat=True)
            .distinct()
        )
        values = [str(v) for v in values if v not in [None, '']]
    return JsonResponse({'values': values})

@require_GET
def ajax_em_unique_values(request):
    field = request.GET.get('field')
    allowed_fields = ['code_em', 'libelle_standard']
    values = []
    if field in allowed_fields:
        values = list(
            EM.objects
            .values_list(field, flat=True)
            .distinct()
        )
        values = [str(v) for v in values if v not in [None, '']]
    return JsonResponse({'values': values})


@require_GET
def ajax_em_filter(request):
    field = request.GET.get('field')
    value = request.GET.get('value')
    if not field or not value:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    allowed_fields = ['code_em', 'libelle_standard']
    if field not in allowed_fields:
        return JsonResponse({'error': 'Field not allowed'}, status=400)

    ems = EM.objects.filter(**{field: value})
    paginator_em = Paginator(ems, 5)
    page_number_em = request.GET.get('page_em', 1)
    ems_page = paginator_em.get_page(page_number_em)
    table_html = render_to_string('pages/partials/em_table_body.html', {'ems': ems_page})
    pagination_html = render_to_string('pages/partials/em_pagination.html', {'ems': ems_page})
    return JsonResponse({'table_body': table_html, 'pagination': pagination_html})