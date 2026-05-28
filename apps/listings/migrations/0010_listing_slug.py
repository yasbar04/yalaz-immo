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
    atomic = False

    dependencies = [
        ('listings', '0009_listing_price_optional'),
    ]

    operations = [
        # Raw SQL: ADD COLUMN IF NOT EXISTS avoids Django's schema editor
        # which would otherwise queue a deferred CREATE INDEX _like that
        # conflicts with the one AlterField also queues (duplicate index bug).
        migrations.RunSQL(
            sql="ALTER TABLE listings_listing ADD COLUMN IF NOT EXISTS slug varchar(280);",
            reverse_sql="ALTER TABLE listings_listing DROP COLUMN IF EXISTS slug;",
        ),
        # Sync Django's migration state (no DB ops)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='listing',
                    name='slug',
                    field=models.SlugField(max_length=280, blank=True, null=True),
                ),
            ],
            database_operations=[],
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        # Drop any pre-existing indexes then recreate cleanly — fully idempotent
        migrations.RunSQL(
            sql="""
                DROP INDEX IF EXISTS listings_listing_slug_984b866c_like;
                ALTER TABLE listings_listing DROP CONSTRAINT IF EXISTS listings_listing_slug_984b866c_uniq;
                DROP INDEX IF EXISTS listings_listing_slug_984b866c_uniq;
                CREATE UNIQUE INDEX listings_listing_slug_984b866c_uniq
                    ON listings_listing (slug);
                CREATE INDEX listings_listing_slug_984b866c_like
                    ON listings_listing (slug varchar_pattern_ops);
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS listings_listing_slug_984b866c_uniq;
                DROP INDEX IF EXISTS listings_listing_slug_984b866c_like;
            """,
        ),
        # Sync Django's migration state to reflect unique=True (no DB ops)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='listing',
                    name='slug',
                    field=models.SlugField(max_length=280, unique=True, blank=True),
                ),
            ],
            database_operations=[],
        ),
    ]
