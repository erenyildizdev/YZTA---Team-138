from rest_framework.throttling import ScopedRateThrottle


class ScopedIPRateThrottle(ScopedRateThrottle):
    """Apply a named DRF throttle scope consistently by client IP."""

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }
