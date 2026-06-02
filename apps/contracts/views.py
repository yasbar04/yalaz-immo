import io
import os
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

from .models import Contract
from .forms import (
    BonVisiteVenteForm, BonVisiteLocationForm,
    MandatVenteForm, MandatLocationForm, MandatRechercheForm,
)

SIGN_LIEU_DATE = {
    'mandat_vente': {
        'client': {'lieu': 'fait_a_mandant', 'date': 'date_mandant', 'label': 'Mandant (Propriétaire)'},
        'agent':  {'lieu': 'fait_a_mandataire', 'date': 'date_mandataire', 'label': 'Mandataire — YALAZ'},
    },
    'mandat_location': {
        'client': {'lieu': 'fait_a_mandant', 'date': 'date_mandant', 'label': 'Mandant (Propriétaire)'},
        'agent':  {'lieu': 'fait_a_mandataire', 'date': 'date_mandataire', 'label': 'Mandataire — YALAZ'},
    },
    'mandat_recherche': {
        'client': {'lieu': 'fait_a_mandant', 'date': 'date_mandant', 'label': 'Mandant (Client)'},
        'agent':  {'lieu': 'fait_a_mandataire', 'date': 'date_mandataire', 'label': 'Mandataire — YALAZ'},
    },
    'bon_visite_vente': {
        'client': {'lieu': 'fait_a_prospect', 'date': 'date_signature_prospect', 'label': 'Prospect (Visiteur)'},
        'agent':  {'lieu': 'fait_a_agence', 'date': 'date_signature_agence', 'label': 'Agence YALAZ'},
    },
    'bon_visite_location': {
        'client': {'lieu': 'fait_a_visiteur', 'date': 'date_signature_visiteur', 'label': 'Visiteur'},
        'agent':  {'lieu': 'fait_a_agent', 'date': 'date_signature_agent', 'label': 'Agent — YALAZ'},
    },
}

FORM_MAP = {
    'bon_visite_vente': BonVisiteVenteForm,
    'bon_visite_location': BonVisiteLocationForm,
    'mandat_vente': MandatVenteForm,
    'mandat_location': MandatLocationForm,
    'mandat_recherche': MandatRechercheForm,
}

TYPE_LABELS = {
    'bon_visite_vente': 'Bon de visite (Vente)',
    'bon_visite_location': 'Bon de visite (Location)',
    'mandat_vente': 'Mandat de vente',
    'mandat_location': 'Mandat de location',
    'mandat_recherche': 'Mandat de recherche',
}

FORM_TEMPLATES = {
    'bon_visite_vente': 'admin/contracts/form_bon_visite_vente.html',
    'bon_visite_location': 'admin/contracts/form_bon_visite_location.html',
    'mandat_vente': 'admin/contracts/form_mandat_vente.html',
    'mandat_location': 'admin/contracts/form_mandat_location.html',
    'mandat_recherche': 'admin/contracts/form_mandat_recherche.html',
}


@staff_member_required
def contracts_list(request):
    contracts = Contract.objects.select_related('created_by').all()
    return render(request, 'admin/contracts/list.html', {'contracts': contracts})


@staff_member_required
def contract_type_selector(request):
    types = [
        {'key': 'bon_visite_vente', 'label': 'Bon de visite', 'sub': 'Vente',
         'desc': "Acte la visite d'un bien mis en vente par un prospect.",
         'icon': 'eye'},
        {'key': 'bon_visite_location', 'label': 'Bon de visite', 'sub': 'Location',
         'desc': "Acte la visite d'un bien mis en location par un visiteur.",
         'icon': 'key'},
        {'key': 'mandat_vente', 'label': 'Mandat de vente', 'sub': 'Immobilier',
         'desc': 'Mission exclusive de commercialisation accordée à YALAZ.',
         'icon': 'home'},
        {'key': 'mandat_location', 'label': 'Mandat de location', 'sub': '',
         'desc': "Mission de recherche d'un locataire pour un bien immobilier.",
         'icon': 'building'},
        {'key': 'mandat_recherche', 'label': 'Mandat de recherche', 'sub': '',
         'desc': "Mission de recherche d'un bien pour le compte d'un client.",
         'icon': 'search'},
    ]
    return render(request, 'admin/contracts/type_selector.html', {'types': types})


@staff_member_required
def contract_create(request, contract_type):
    if contract_type not in FORM_MAP:
        return redirect('contracts_list')

    FormClass = FORM_MAP[contract_type]
    template = FORM_TEMPLATES[contract_type]
    label = TYPE_LABELS[contract_type]

    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            # Serialize dates/times to strings for JSON storage
            cleaned = {}
            for key, value in form.cleaned_data.items():
                if hasattr(value, 'isoformat'):
                    cleaned[key] = value.isoformat()
                else:
                    cleaned[key] = str(value) if value is not None else ''
            # Capture base64 signature images from canvas
            client_sig = request.POST.get('client_signature', '')
            agent_sig  = request.POST.get('agent_signature', '')
            if client_sig.startswith('data:image/'):
                cleaned['client_signature'] = client_sig
            if agent_sig.startswith('data:image/'):
                cleaned['agent_signature'] = agent_sig
            contract = Contract.objects.create(
                type=contract_type,
                created_by=request.user,
                data=cleaned,
            )
            return redirect('contract_sign', pk=contract.pk)
    else:
        # Pre-fill agent name from logged-in user
        initial = {}
        full_name = request.user.get_full_name() or request.user.username
        if 'agent_nom' in FormClass().fields:
            initial['agent_nom'] = full_name
        if 'agent_accompagnant' in FormClass().fields:
            initial['agent_accompagnant'] = full_name
        form = FormClass(initial=initial)

    return render(request, template, {'form': form, 'label': label, 'contract_type': contract_type})


@staff_member_required
def contract_sign(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    FormClass = FORM_MAP[contract.type]

    if request.method == 'POST':
        client_sig = request.POST.get('client_signature', '')
        agent_sig  = request.POST.get('agent_signature', '')
        data = contract.data.copy()
        if client_sig.startswith('data:image/'):
            data['client_signature'] = client_sig
        if agent_sig.startswith('data:image/'):
            data['agent_signature'] = agent_sig
        cfg = SIGN_LIEU_DATE.get(contract.type, {})
        for party in ('client', 'agent'):
            for slot in ('lieu', 'date'):
                field_name = cfg.get(party, {}).get(slot)
                if field_name:
                    val = request.POST.get(field_name, '').strip()
                    if val:
                        data[field_name] = val
        contract.data = data
        contract.save()
        return redirect('contract_pdf', pk=contract.pk)

    # Build recap: list of (label, value) from form field definitions
    form = FormClass(initial=contract.data)
    SKIP = {'client_signature', 'agent_signature'}
    recap = []
    for name, field in form.fields.items():
        if name in SKIP:
            continue
        value = contract.data.get(name, '')
        if value:
            recap.append({'label': field.label, 'value': str(value)})

    client_sig_label = {
        'bon_visite_vente': 'Prospect (Visiteur)',
        'bon_visite_location': 'Visiteur',
        'mandat_vente': 'Mandant (Propriétaire)',
        'mandat_location': 'Mandant (Propriétaire)',
        'mandat_recherche': 'Mandant (Client)',
    }.get(contract.type, 'Client')

    sign_config = SIGN_LIEU_DATE.get(contract.type, {})

    return render(request, 'admin/contracts/sign.html', {
        'contract': contract,
        'recap': recap,
        'client_sig_label': client_sig_label,
        'sign_config': sign_config,
    })


@staff_member_required
def contract_detail(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    return render(request, 'admin/contracts/detail.html', {'contract': contract})


def _logo_b64():
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_yalaz.png')
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()
    return None


@staff_member_required
def contract_pdf(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    html_string = render_to_string(
        contract.get_pdf_template(),
        {'contract': contract, 'd': contract.data, 'logo_b64': _logo_b64()},
        request=request,
    )
    buffer = io.BytesIO()
    from xhtml2pdf import pisa
    result = pisa.CreatePDF(html_string, dest=buffer, encoding='utf-8')
    if result.err:
        return HttpResponse(html_string, content_type='text/html')
    pdf_bytes = buffer.getvalue()
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f'{contract.reference}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@staff_member_required
def contract_delete(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == 'POST':
        contract.delete()
        return redirect('contracts_list')
    return render(request, 'admin/contracts/confirm_delete.html', {'contract': contract})
