import calendar
from datetime import date
from django.core.management.base import BaseCommand
from apps.core.models import FinancialTransaction


def _add_months(d, months):
    """Add N months to a date, clamping to last day of month if needed."""
    total = d.month - 1 + months
    year  = d.year + total // 12
    month = total % 12 + 1
    day   = min(d.day, calendar.monthrange(year, month)[1])
    return d.replace(year=year, month=month, day=day)


def _next_date(from_date, recurrence):
    if recurrence == 'monthly':
        return _add_months(from_date, 1)
    if recurrence == 'quarterly':
        return _add_months(from_date, 3)
    if recurrence == 'yearly':
        return from_date.replace(year=from_date.year + 1)
    return None


class Command(BaseCommand):
    help = 'Génère les transactions récurrentes dont la prochaine échéance est atteinte.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les transactions qui seraient créées sans les enregistrer.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today   = date.today()
        created = 0
        skipped = 0

        # Transactions source : récurrentes, sans parent (= originales)
        sources = FinancialTransaction.objects.filter(
            is_recurring=True,
            recurring_parent=None,
        ).prefetch_related('recurring_children')

        for source in sources:
            if not source.recurrence:
                skipped += 1
                continue

            # Date de référence = date de création (champ created_at -> date)
            # On cherche la plus récente occurrence dans la chaîne
            latest_date = source.created_at.date()

            children_dates = source.recurring_children.values_list('transaction_date', flat=True)
            if children_dates:
                latest_date = max(latest_date, max(children_dates))

            next_due = _next_date(latest_date, source.recurrence)
            if next_due is None:
                skipped += 1
                continue

            # Pas encore due
            if next_due > today:
                skipped += 1
                continue

            # Déjà générée pour cette date ?
            already_exists = source.recurring_children.filter(
                transaction_date=next_due
            ).exists()
            if already_exists:
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(
                    f'[DRY-RUN] {source} → {next_due} ({source.recurrence})'
                )
                created += 1
                continue

            # Création de la nouvelle occurrence
            FinancialTransaction.objects.create(
                type=source.type,
                status='pending',          # en attente de validation
                amount=source.amount,
                description=source.description,
                category=source.category,
                property_price=source.property_price,
                commission_percentage=source.commission_percentage,
                payment_source=source.payment_source,
                owner_amount=source.owner_amount,
                client_amount=source.client_amount,
                listing=source.listing,
                created_by=source.created_by,
                assigned_to=source.assigned_to,
                transaction_date=next_due,
                notes=f'Générée automatiquement depuis #{source.pk}',
                is_recurring=False,        # les enfants ne se régénèrent pas eux-mêmes
                recurring_parent=source,
            )
            created += 1
            self.stdout.write(
                self.style.SUCCESS(f'Créée : {source.description} → {next_due}')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTerminé — {created} transaction(s) créée(s), {skipped} ignorée(s).'
            )
        )
