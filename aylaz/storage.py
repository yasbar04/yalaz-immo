from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class RelaxedManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """ManifestStaticFilesStorage sans erreur sur les fichiers manquants."""
    manifest_strict = False
