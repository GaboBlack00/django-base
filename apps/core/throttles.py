"""Custom throttle classes for rate-limiting specific endpoints.

Rates are configured in ``DEFAULT_THROTTLE_RATES`` in
``config/settings/base.py`` under the matching scope name.
"""

from rest_framework.throttling import UserRateThrottle


class LoginRateThrottle(UserRateThrottle):
    """Limit login attempts per user/IP to the rate configured in ``login`` scope.

    Connected to ``LoginView`` to prevent brute-force attacks.
    """

    scope = "login"