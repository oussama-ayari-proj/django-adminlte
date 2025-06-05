from django.shortcuts import render
from django.core.paginator import Paginator
from .models import UF, Sejour, EM, Pole,ETB
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET

def index(request):
    ufs = UF.objects.all()
    sejours = Sejour.objects.all()
    ems = EM.objects.all()
    poles = Pole.objects.all()
    etbs = ETB.objects.all()

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

    # Pagination for Poles
    paginator_poles = Paginator(poles, 5)
    page_number_pole = request.GET.get('page_pole')
    poles_page = paginator_poles.get_page(page_number_pole)

    # Pagination for ETB
    paginator_etbs = Paginator(etbs, 5)
    page_number_etb = request.GET.get('page_etb')
    etbs_page = paginator_etbs.get_page(page_number_etb)

    return render(request, 'pages/index.html', {
        'ufs': ufs_page,
        'sejours': sejours_page,
        'ems': ems_page,
        'poles': poles_page,
        'etbs': etbs_page
    })

# AJAX views for pagination
def ajax_ufs_pagination(request):
    ufs = UF.objects.all()
    paginator_ufs = Paginator(ufs, 5)
    page_number_uf = request.GET.get('page_uf')
    field = request.GET.get('field')
    value = request.GET.get('value')
    if not field or not value:
        field = None
    if field and value:
        ufs = ufs.filter(**{field: value})
        paginator_ufs = Paginator(ufs, 5)
    ufs_page = paginator_ufs.get_page(page_number_uf)
    table_html = render_to_string('pages/partials/uf_table_body.html', {'ufs': ufs_page})
    pagination_html = render_to_string('pages/partials/uf_pagination.html', {'ufs': ufs_page})
    return JsonResponse({'table_body': table_html, 'pagination': pagination_html})

def ajax_sejours_pagination(request):
    sejours = Sejour.objects.all()
    paginator_sejours = Paginator(sejours, 10)
    page_number_sejour = request.GET.get('page_sejour')
    field = request.GET.get('field')
    value = request.GET.get('value')
    if not field or not value:
        field = None
    if field and value:
        sejours = sejours.filter(**{field: value})
        paginator_sejours = Paginator(sejours, 10)
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
    print(f"Field: {field}, Value: {value},Page: {page_number_em}")
    if not field or not value:
        field = None
    if field and value:
        em = em.filter(**{field: value})
        paginator_em = Paginator(em, 5)
    ems_page = paginator_em.get_page(page_number_em)
    table_html = render_to_string('pages/partials/em_table_body.html', {'ems': ems_page})
    pagination_html = render_to_string('pages/partials/em_pagination.html', {'ems': ems_page})
    return JsonResponse({'table_body': table_html, 'pagination': pagination_html})

def ajax_poles_pagination(request):
    poles = Pole.objects.all()
    paginator_poles = Paginator(poles, 5)
    page_number_pole = request.GET.get('page_pole')
    field = request.GET.get('field')
    value = request.GET.get('value')
    if not field or not value:
        field = None
    if field and value:
        poles = poles.filter(**{field: value})
        paginator_poles = Paginator(poles, 5)
    poles_page = paginator_poles.get_page(page_number_pole)
    table_html = render_to_string('pages/partials/pole_table_body.html', {'poles': poles_page})
    pagination_html = render_to_string('pages/partials/pole_pagination.html', {'poles': poles_page})
    return JsonResponse({'table_body': table_html, 'pagination': pagination_html})

def ajax_etbs_pagination(request):
    etbs = ETB.objects.all()
    paginator_etbs = Paginator(etbs, 5)
    page_number_etb = request.GET.get('page_etb')
    field = request.GET.get('field')
    value = request.GET.get('value')
    if not field or not value:
        field = None
    if field and value:
        etbs = etbs.filter(**{field: value})
        paginator_etbs = Paginator(etbs, 5)
    etbs_page = paginator_etbs.get_page(page_number_etb)
    table_html = render_to_string('pages/partials/etb_table_body.html', {'etbs': etbs_page})
    pagination_html = render_to_string('pages/partials/etb_pagination.html', {'etbs': etbs_page})
    return JsonResponse({'table_body': table_html, 'pagination': pagination_html})


# AJAX views for unique values
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
def ajax_pole_unique_values(request):
    field = request.GET.get('field')
    allowed_fields = ['code_pole', 'libelle_standard']
    values = []
    if field in allowed_fields:
        values = list(
            Pole.objects
            .values_list(field, flat=True)
            .distinct()
        )
        values = [str(v) for v in values if v not in [None, '']]
    return JsonResponse({'values': values})

@require_GET
def ajax_etb_unique_values(request):
    field = request.GET.get('field')
    allowed_fields = ['code_etb', 'libelle_standard']
    values = []
    if field in allowed_fields:
        values = list(
            ETB.objects
            .values_list(field, flat=True)
            .distinct()
        )
        values = [str(v) for v in values if v not in [None, '']]
    return JsonResponse({'values': values})


# Filter views for AJAX requests
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

@require_GET
def ajax_uf_filter(request):
    field = request.GET.get('field')
    value = request.GET.get('value')
    if not field or not value:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    allowed_fields = [
        'libelle_standard', 'code_uf', 'code_etb', 'code_pole', 'heb',
        'type_uf', 'libelle_type_uf', 'type_activite', 'libelle_type_activite'
    ]
    if field not in allowed_fields:
        return JsonResponse({'error': 'Field not allowed'}, status=400)

    ufs = UF.objects.filter(**{field: value})
    paginator_ufs = Paginator(ufs, 5)
    page_number_uf = request.GET.get('page_uf', 1)
    ufs_page = paginator_ufs.get_page(page_number_uf)
    table_html = render_to_string('pages/partials/uf_table_body.html', {'ufs': ufs_page})
    pagination_html = render_to_string('pages/partials/uf_pagination.html', {'ufs': ufs_page})
    return JsonResponse({'table_body': table_html, 'pagination': pagination_html})

@require_GET
def ajax_sejour_filter(request):
    field = request.GET.get('field')
    value = request.GET.get('value')
    if not field or not value:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    allowed_fields = [
        'num_sequence', 'code_uf', 'code_em', 'duree_sejour', 'type_sejour',
        'date_sortie', 'ghs', 'sexe', 'age_entree', 'semaine_entree', 'date_entree'
    ]
    if field not in allowed_fields:
        return JsonResponse({'error': 'Field not allowed'}, status=400)

    sejours = Sejour.objects.filter(**{field: value})
    paginator_sejours = Paginator(sejours, 10)
    page_number_sejour = request.GET.get('page_sejour', 1)
    sejours_page = paginator_sejours.get_page(page_number_sejour)
    table_html = render_to_string('pages/partials/sejour_table_body.html', {'sejours': sejours_page})
    pagination_html = render_to_string('pages/partials/sejour_pagination.html', {'sejours': sejours_page})
    return JsonResponse({'table_body': table_html, 'pagination': pagination_html})

@require_GET
def ajax_pole_filter(request):
    field = request.GET.get('field')
    value = request.GET.get('value')
    if not field or not value:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    allowed_fields = ['code_pole', 'libelle_standard']
    if field not in allowed_fields:
        return JsonResponse({'error': 'Field not allowed'}, status=400)

    poles = Pole.objects.filter(**{field: value})
    paginator_poles = Paginator(poles, 5)
    page_number_pole = request.GET.get('page_pole', 1)
    poles_page = paginator_poles.get_page(page_number_pole)
    table_html = render_to_string('pages/partials/pole_table_body.html', {'poles': poles_page})
    pagination_html = render_to_string('pages/partials/pole_pagination.html', {'poles': poles_page})
    return JsonResponse({'table_body': table_html, 'pagination': pagination_html})

@require_GET
def ajax_etb_filter(request):
    field = request.GET.get('field')
    value = request.GET.get('value')
    if not field or not value:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    allowed_fields = ['code_etb', 'libelle_standard']
    if field not in allowed_fields:
        return JsonResponse({'error': 'Field not allowed'}, status=400)

    etbs = ETB.objects.filter(**{field: value})
    paginator_etbs = Paginator(etbs, 5)
    page_number_etb = request.GET.get('page_etb', 1)
    etbs_page = paginator_etbs.get_page(page_number_etb)
    table_html = render_to_string('pages/partials/etb_table_body.html', {'etbs': etbs_page})
    pagination_html = render_to_string('pages/partials/etb_pagination.html', {'etbs': etbs_page})
    return JsonResponse({'table_body': table_html, 'pagination': pagination_html})