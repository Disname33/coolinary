from django.views.debug import get_exception_reporter_filter


class HideSettingsOnErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 500:
            settings_filter = get_exception_reporter_filter(request)
            settings_filter.get_post_parameters = lambda: {}
            settings_filter.get_settings = lambda: {}
        return response
