from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_userprofile_password_change_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                blank=True,
                choices=[('admin', 'Admin'), ('staff', 'Staff')],
                default='staff',
                help_text='Rôle dans le back office (admin ou staff)',
                max_length=10,
            ),
        ),
    ]
