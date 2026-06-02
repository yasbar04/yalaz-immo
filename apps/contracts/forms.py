from django import forms
from django.utils import timezone


PIECE_IDENTITE_CHOICES = [('CIN', 'CIN'), ('passeport', 'Passeport')]
EXCLUSIVITE_CHOICES = [('exclusif', 'Exclusif'), ('non_exclusif', 'Non exclusif')]
REMUNERATION_TYPE_CHOICES = [('percentage', '% TTC du prix'), ('forfait', 'MAD TTC (forfait)')]
MEUBLE_CHOICES = [('oui', 'Oui'), ('non', 'Non')]


def date_widget():
    return forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})

def time_widget():
    return forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})

def text_widget(placeholder=''):
    return forms.TextInput(attrs={'class': 'form-control', 'placeholder': placeholder})

def number_widget(placeholder=''):
    return forms.NumberInput(attrs={'class': 'form-control', 'placeholder': placeholder, 'min': '0'})

def select_widget():
    return forms.Select(attrs={'class': 'form-control'})

def textarea_widget(rows=3):
    return forms.Textarea(attrs={'class': 'form-control', 'rows': rows})


class BonVisiteVenteForm(forms.Form):
    # Section 1 — Prospect
    nom_prenom          = forms.CharField(label='Nom & Prénom', widget=text_widget())
    cin_passeport       = forms.CharField(label='CIN / Passeport', widget=text_widget())
    telephone_prospect  = forms.CharField(label='Téléphone', widget=text_widget())

    # Section 2 — Bien visité + Agent
    type_bien           = forms.CharField(label='Type de bien', widget=text_widget('Ex : Appartement, Villa…'))
    adresse_bien        = forms.CharField(label='Adresse du bien', widget=text_widget())
    reference_bien      = forms.CharField(label='Référence du bien', widget=text_widget(), required=False)
    date_visite         = forms.DateField(label='Date de la visite', widget=date_widget(), initial=timezone.now().date)
    heure_visite        = forms.TimeField(label='Heure de la visite', widget=time_widget(), initial='10:00')
    agent_accompagnant  = forms.CharField(label='Nom de l\'agent', widget=text_widget())
    agent_cin           = forms.CharField(label='CIN de l\'agent', widget=text_widget(), required=False)
    agent_telephone     = forms.CharField(label='Téléphone de l\'agent', widget=text_widget('+212 648 707 583'),
                                          required=False, initial='+212 648 707 583')

    # Section 5 — Rémunération
    remuneration_type       = forms.ChoiceField(label='Type de rémunération', choices=REMUNERATION_TYPE_CHOICES,
                                                widget=select_widget(), required=False)
    remuneration_percentage = forms.DecimalField(label='Pourcentage (%)', max_digits=5, decimal_places=2,
                                                 required=False, widget=number_widget('Ex : 2.5'))
    remuneration_forfait    = forms.DecimalField(label='Forfait (MAD)', max_digits=12, decimal_places=2,
                                                 required=False, widget=number_widget('Ex : 50000'))

    # Lieu & date
    fait_a_prospect        = forms.CharField(label='Fait à (Prospect)', widget=text_widget('Casablanca'), required=False)
    date_signature_prospect = forms.DateField(label='Le (Prospect)', widget=date_widget(), required=False,
                                              initial=timezone.now().date)
    fait_a_agence          = forms.CharField(label='Fait à (Agence)', widget=text_widget('Casablanca'),
                                             required=False, initial='Casablanca')
    date_signature_agence  = forms.DateField(label='Le (Agence)', widget=date_widget(), required=False,
                                             initial=timezone.now().date)


class BonVisiteLocationForm(forms.Form):
    # Section 1 — Bien
    reference_bien      = forms.CharField(label='Référence du bien', widget=text_widget(), required=False)
    type_bien           = forms.CharField(label='Type de bien', widget=text_widget('Ex : Appartement, Villa…'))
    adresse_bien        = forms.CharField(label='Adresse', widget=text_widget())
    ville_quartier      = forms.CharField(label='Ville / Quartier', widget=text_widget(), required=False)
    surface             = forms.CharField(label='Surface (m²)', widget=text_widget(), required=False)
    nb_pieces           = forms.CharField(label='Nombre de pièces', widget=text_widget(), required=False)
    etage               = forms.CharField(label='Étage', widget=text_widget(), required=False)
    meuble              = forms.ChoiceField(label='Meublé', choices=MEUBLE_CHOICES, widget=select_widget(), required=False)
    loyer_mensuel       = forms.DecimalField(label='Loyer mensuel (MAD)', max_digits=12, decimal_places=2,
                                             required=False, widget=number_widget())
    charges_mensuelles  = forms.DecimalField(label='Charges mensuelles (MAD)', max_digits=12, decimal_places=2,
                                             required=False, widget=number_widget())
    depot_garantie      = forms.DecimalField(label='Dépôt de garantie (MAD)', max_digits=12, decimal_places=2,
                                             required=False, widget=number_widget())

    # Section 2 — Visite & Agent
    date_visite         = forms.DateField(label='Date de la visite', widget=date_widget(), initial=timezone.now().date)
    heure_visite        = forms.TimeField(label='Heure de la visite', widget=time_widget(), initial='10:00')
    agent_nom           = forms.CharField(label='Nom de l\'agent', widget=text_widget())
    agent_cin           = forms.CharField(label='CIN de l\'agent', widget=text_widget(), required=False)
    agent_telephone     = forms.CharField(label='Téléphone de l\'agent', widget=text_widget('+212 648 707 583'),
                                          required=False, initial='+212 648 707 583')
    duree_visite        = forms.CharField(label='Durée de la visite', widget=text_widget('Ex : 30 min'), required=False)

    # Section 3 — Visiteur
    visiteur_nom_prenom     = forms.CharField(label='Nom & Prénom du visiteur', widget=text_widget())
    visiteur_telephone      = forms.CharField(label='Téléphone', widget=text_widget())
    visiteur_piece_identite = forms.ChoiceField(label="Pièce d'identité", choices=PIECE_IDENTITE_CHOICES,
                                                widget=select_widget())
    visiteur_num_piece      = forms.CharField(label="N° de pièce d'identité", widget=text_widget(), required=False)

    # Lieu & date
    fait_a_visiteur        = forms.CharField(label='Fait à (Visiteur)', widget=text_widget('Casablanca'), required=False)
    date_signature_visiteur = forms.DateField(label='Le (Visiteur)', widget=date_widget(), required=False,
                                              initial=timezone.now().date)
    fait_a_agent           = forms.CharField(label='Fait à (Agent)', widget=text_widget('Casablanca'),
                                             required=False, initial='Casablanca')
    date_signature_agent   = forms.DateField(label='Le (Agent)', widget=date_widget(), required=False,
                                             initial=timezone.now().date)


class MandatVenteForm(forms.Form):
    # Section 1 — Mandant (Propriétaire)
    mandant_nom       = forms.CharField(label='Nom & Prénom / Société', widget=text_widget())
    mandant_cin       = forms.CharField(label='CIN / RC', widget=text_widget(), required=False)
    mandant_telephone = forms.CharField(label='Téléphone', widget=text_widget())

    # Section 1 — Mandataire (Agent)
    agent_nom       = forms.CharField(label='Nom de l\'agent', widget=text_widget())
    agent_cin       = forms.CharField(label='CIN de l\'agent', widget=text_widget(), required=False)
    agent_telephone = forms.CharField(label='Téléphone de l\'agent', widget=text_widget('+212 648 707 583'),
                                      required=False, initial='+212 648 707 583')

    # Section 2 — Bien
    bien_type           = forms.CharField(label='Type de bien', widget=text_widget('Ex : Appartement, Villa…'))
    bien_adresse        = forms.CharField(label='Adresse du bien', widget=text_widget())
    bien_surface        = forms.CharField(label='Surface (m²)', widget=text_widget(), required=False)
    bien_titre_foncier  = forms.CharField(label='Titre foncier', widget=text_widget(), required=False)
    prix_net_vendeur    = forms.DecimalField(label='Prix net vendeur souhaité (MAD)', max_digits=15, decimal_places=2,
                                             required=False, widget=number_widget())

    # Section 4 — Durée
    duree_mois = forms.IntegerField(label='Durée du mandat (mois)', min_value=1,
                                    widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': '3'}))

    # Section 5 — Rémunération
    remuneration_type       = forms.ChoiceField(label='Type de rémunération', choices=REMUNERATION_TYPE_CHOICES,
                                                widget=select_widget(), required=False)
    remuneration_percentage = forms.DecimalField(label='Pourcentage (%)', max_digits=5, decimal_places=2,
                                                 required=False, widget=number_widget('Ex : 2.5'))
    remuneration_forfait    = forms.DecimalField(label='Forfait (MAD)', max_digits=12, decimal_places=2,
                                                 required=False, widget=number_widget())

    # Section 6 — Exclusivité
    exclusivite = forms.ChoiceField(label='Exclusivité', choices=EXCLUSIVITE_CHOICES, widget=select_widget())

    # Lieu & date
    fait_a_mandant    = forms.CharField(label='Fait à (Mandant)', widget=text_widget('Casablanca'), required=False)
    date_mandant      = forms.DateField(label='Le (Mandant)', widget=date_widget(), required=False,
                                        initial=timezone.now().date)
    fait_a_mandataire = forms.CharField(label='Fait à (Mandataire)', widget=text_widget('Casablanca'),
                                        required=False, initial='Casablanca')
    date_mandataire   = forms.DateField(label='Le (Mandataire)', widget=date_widget(), required=False,
                                        initial=timezone.now().date)


class MandatLocationForm(forms.Form):
    # Section 1 — Mandant (Propriétaire)
    mandant_nom       = forms.CharField(label='Nom & Prénom / Société', widget=text_widget())
    mandant_cin       = forms.CharField(label='CIN / RC', widget=text_widget(), required=False)
    mandant_telephone = forms.CharField(label='Téléphone', widget=text_widget())

    # Section 1 — Mandataire (Agent)
    agent_nom       = forms.CharField(label='Nom de l\'agent', widget=text_widget())
    agent_cin       = forms.CharField(label='CIN de l\'agent', widget=text_widget(), required=False)
    agent_telephone = forms.CharField(label='Téléphone de l\'agent', widget=text_widget('+212 648 707 583'),
                                      required=False, initial='+212 648 707 583')

    # Section 2 — Bien
    bien_type               = forms.CharField(label='Type de bien', widget=text_widget())
    bien_adresse            = forms.CharField(label='Adresse du bien', widget=text_widget())
    bien_surface            = forms.CharField(label='Surface (m²)', widget=text_widget(), required=False)
    bien_etage              = forms.CharField(label='Étage / N°', widget=text_widget(), required=False)
    bien_etat_equipements   = forms.CharField(label='État / Équipements', widget=text_widget(), required=False)
    loyer_mensuel_souhaite  = forms.DecimalField(label='Loyer mensuel souhaité (MAD)', max_digits=12,
                                                 decimal_places=2, required=False, widget=number_widget())

    # Section 5 — Durée
    duree_mois = forms.IntegerField(label='Durée du mandat (mois)', min_value=1,
                                    widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': '3'}))

    # Section 6 — Exclusivité
    exclusivite = forms.ChoiceField(label='Exclusivité', choices=EXCLUSIVITE_CHOICES, widget=select_widget())

    # Lieu & date
    fait_a_mandant    = forms.CharField(label='Fait à (Mandant)', widget=text_widget('Casablanca'), required=False)
    date_mandant      = forms.DateField(label='Le (Mandant)', widget=date_widget(), required=False,
                                        initial=timezone.now().date)
    fait_a_mandataire = forms.CharField(label='Fait à (Mandataire)', widget=text_widget('Casablanca'),
                                        required=False, initial='Casablanca')
    date_mandataire   = forms.DateField(label='Le (Mandataire)', widget=date_widget(), required=False,
                                        initial=timezone.now().date)


class MandatRechercheForm(forms.Form):
    # Section 1 — Mandant (Client)
    mandant_nom       = forms.CharField(label='Nom & Prénom / Société', widget=text_widget())
    mandant_cin       = forms.CharField(label='CIN / RC', widget=text_widget(), required=False)
    mandant_telephone = forms.CharField(label='Téléphone', widget=text_widget())

    # Section 1 — Mandataire (Agent)
    agent_nom       = forms.CharField(label='Nom & Prénom de l\'agent', widget=text_widget())
    agent_cin       = forms.CharField(label='CIN de l\'agent', widget=text_widget(), required=False)
    agent_telephone = forms.CharField(label='Téléphone de l\'agent', widget=text_widget('+212 648 707 583'),
                                      required=False, initial='+212 648 707 583')

    # Section 3 — Critères de recherche
    type_bien_recherche  = forms.CharField(label='Type de bien recherché', widget=text_widget())
    localisation_souhaitee = forms.CharField(label='Localisation souhaitée', widget=text_widget())
    surface_minimum      = forms.CharField(label='Surface minimum (m²)', widget=text_widget(), required=False)
    budget               = forms.DecimalField(label='Budget indicatif (MAD)', max_digits=15, decimal_places=2,
                                              required=False, widget=number_widget())
    nb_pieces            = forms.CharField(label='Nombre de pièces', widget=text_widget(), required=False)
    autres_criteres      = forms.CharField(label='Autres critères / précisions', widget=textarea_widget(2), required=False)

    # Section 5 — Durée
    duree_mois           = forms.IntegerField(label='Durée du mandat (mois)', min_value=1,
                                              widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': '3'}))
    periode_reconduction = forms.IntegerField(label='Période de reconduction (mois)', min_value=1, required=False,
                                              widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}))

    # Section 6 — Rémunération
    remuneration_percentage = forms.DecimalField(label='Pourcentage (%)', max_digits=5, decimal_places=2,
                                                 required=False, widget=number_widget('Ex : 2.5'))
    remuneration_forfait    = forms.DecimalField(label='Forfait MAD TTC', max_digits=12, decimal_places=2,
                                                 required=False, widget=number_widget())

    # Section 7 — Exclusivité
    exclusivite = forms.ChoiceField(label='Exclusivité', choices=EXCLUSIVITE_CHOICES, widget=select_widget())

    # Section 9 — Tribunal
    tribunal_competent = forms.CharField(label='Tribunaux compétents de', widget=text_widget('Casablanca'),
                                         required=False, initial='Casablanca')

    # Lieu & date
    fait_a_mandant    = forms.CharField(label='Fait à (Mandant)', widget=text_widget('Casablanca'), required=False)
    date_mandant      = forms.DateField(label='Le (Mandant)', widget=date_widget(), required=False,
                                        initial=timezone.now().date)
    fait_a_mandataire = forms.CharField(label='Fait à (Mandataire)', widget=text_widget('Casablanca'),
                                        required=False, initial='Casablanca')
    date_mandataire   = forms.DateField(label='Le (Mandataire)', widget=date_widget(), required=False,
                                        initial=timezone.now().date)
