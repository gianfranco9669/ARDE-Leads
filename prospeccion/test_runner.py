from django.test.runner import DiscoverRunner

class ProspeccionDiscoverRunner(DiscoverRunner):
    """Ensure `python manage.py test` runs the app suite when no labels are passed."""
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        labels = test_labels or ['prospeccion']
        return super().run_tests(labels, extra_tests=extra_tests, **kwargs)
