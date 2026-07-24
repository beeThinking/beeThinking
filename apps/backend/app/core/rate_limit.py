from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings


def get_rate_limit_key(request) -> str:
    settings = get_settings()
    remote_address = get_remote_address(request)
    if (
        settings.TRUST_PROXY_HEADERS
        and remote_address in settings.trusted_proxy_ips_set
    ):
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",", 1)[0].strip()
    return remote_address


limiter = Limiter(key_func=get_rate_limit_key, headers_enabled=True)
