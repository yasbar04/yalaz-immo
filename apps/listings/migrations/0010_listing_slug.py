from django.db import migrations, models
from django.utils.text import slugify

_PROPERTY_SLUG = {
    'apartment': 'appartement', 'house': 'maison', 'villa': 'villa',
    'land': 'terrain', 'office': 'bureau', 'commercial': 'local-commercial',
}
_TYPE_SLUG = {'sale': 'vente', 'rent': 'location'}


def populate_slugs(apps, schema_editor):
    Listing = apps.get_model('listings', 'Listing')
    for listing in Listing.objects.all():
        prop = _PROPERTY_SLUG.get(listing.property_type, listing.property_type)
        typ = _TYPE_SLUG.get(listing.listing_type, listing.listing_type)
        city = slugify(listing.city or 'maroc')
        listing.slug = f"{prop}-{typ}-{city}-{listing.pk}"
        listing.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0009_listing_price_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='slug',
            field=models.SlugField(max_length=280, blank=True, null=True),
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        # Drop any indexes left by a partial migration run on prod (idempotent)
        migrations.RunSQL(
            sql="""
                DROP INDEX IF EXISTS listings_listing_slug_984b866c_like;
                DROP INDEX IF EXISTS listings_listing_slug_984b866c_uniq;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='listing',
            name='slug',
            field=models.SlugField(max_length=280, unique=True, blank=True),
        ),
    ]
