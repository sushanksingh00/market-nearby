from django.conf import settings
from django.http import HttpResponseRedirect


class LocalhostRedirectMiddleware:
    """Redirect 0.0.0.0 to localhost in development for trusted-origin APIs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            full_host = request.get_host().strip()
            host = full_host.split(":")[0].strip().lower()
            if host == "0.0.0.0":
                if ":" in full_host:
                    port = full_host.split(":", 1)[1]
                else:
                    port = request.get_port()
                target = f"{request.scheme}://localhost:{port}{request.get_full_path()}"
                return HttpResponseRedirect(target)
        return self.get_response(request)