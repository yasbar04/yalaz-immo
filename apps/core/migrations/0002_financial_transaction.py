# Generated migration for FinancialTransaction model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('listings', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FinancialTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('income', 'Revenus'), ('expense', 'Dépenses'), ('commission', 'Commission'), ('refund', 'Remboursement')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('completed', 'Complété'), ('cancelled', 'Annulé')], default='completed', max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, help_text='Montant en DH', max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ('description', models.CharField(help_text='Exemple: Vidéo 500dh, Commission vente bien, etc.', max_length=255)),
                ('category', models.CharField(blank=True, help_text='Catégorie: Vidéo, Photographie, Commission, etc.', max_length=100)),
                ('transaction_date', models.DateField(default=django.utils.timezone.now, help_text='Date de la transaction')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, help_text='Notes supplémentaires')),
                ('assigned_to', models.ForeignKey(blank=True, help_text='Personne affectée à cette transaction', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='financial_transactions_assigned', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(help_text='Personne qui a enregistré la transaction', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='financial_transactions_created', to=settings.AUTH_USER_MODEL)),
                ('listing', models.ForeignKey(blank=True, help_text='Bien immobilier associé (si applicable)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='financial_transactions', to='listings.listing')),
            ],
            options={
                'verbose_name': 'Transaction Financière',
                'verbose_name_plural': 'Transactions Financières',
                'ordering': ['-transaction_date', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='financialtransaction',
            index=models.Index(fields=['-transaction_date'], name='core_financi_transac_idx'),
        ),
        migrations.AddIndex(
            model_name='financialtransaction',
            index=models.Index(fields=['type', 'status'], name='core_financi_type_st_idx'),
        ),
    ]
