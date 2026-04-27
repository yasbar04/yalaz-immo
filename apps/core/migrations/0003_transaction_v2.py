from django.db import migrations, models
import django.core.validators


def migrate_type_values(apps, schema_editor):
    FinancialTransaction = apps.get_model('core', 'FinancialTransaction')
    FinancialTransaction.objects.filter(type__in=['income', 'commission']).update(type='entry')
    FinancialTransaction.objects.filter(type__in=['expense', 'refund']).update(type='exit')
    FinancialTransaction.objects.filter(category='').update(category='autre')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_financial_transaction'),
    ]

    operations = [
        # Convertir les anciennes valeurs de type avant de changer le champ
        migrations.RunPython(migrate_type_values, migrations.RunPython.noop),

        migrations.AlterField(
            model_name='financialtransaction',
            name='type',
            field=models.CharField(
                choices=[('entry', 'Entrée'), ('exit', 'Sortie')],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='financialtransaction',
            name='category',
            field=models.CharField(
                choices=[
                    ('commission_vente', 'Commission vente'),
                    ('commission_location', 'Commission location'),
                    ('marketing', 'Marketing / Réseaux sociaux'),
                    ('video_shooting', 'Vidéo / Shooting'),
                    ('frais_divers', 'Frais divers'),
                    ('autre', 'Autre'),
                ],
                default='autre',
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name='financialtransaction',
            name='property_price',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Prix total du bien (pour calcul commission)',
                max_digits=15,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AddField(
            model_name='financialtransaction',
            name='commission_percentage',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Pourcentage de commission (ex: 2.5)',
                max_digits=5,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AddField(
            model_name='financialtransaction',
            name='payment_source',
            field=models.CharField(
                blank=True,
                choices=[('owner', 'Propriétaire'), ('client', 'Client'), ('both', 'Les deux')],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='financialtransaction',
            name='owner_amount',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Montant payé par le propriétaire',
                max_digits=12,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AddField(
            model_name='financialtransaction',
            name='client_amount',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Montant payé par le client',
                max_digits=12,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
    ]
