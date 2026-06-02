from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('bon_visite_vente', 'Bon de visite (Vente)'), ('bon_visite_location', 'Bon de visite (Location)'), ('mandat_vente', 'Mandat de vente'), ('mandat_location', 'Mandat de location'), ('mandat_recherche', 'Mandat de recherche')], max_length=50)),
                ('reference', models.CharField(blank=True, max_length=50, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('data', models.JSONField(default=dict)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contracts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Contrat',
                'verbose_name_plural': 'Contrats',
                'ordering': ['-created_at'],
            },
        ),
    ]
