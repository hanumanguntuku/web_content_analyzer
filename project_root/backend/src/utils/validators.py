from urllib.parse import urlparse
import ipaddress

PRIVATE_NETWORKS = [
    ('10.0.0.0', '255.0.0.0'),
    ('172.16.0.0', '255.240.0.0'),
    ('192.168.0.0', '255.255.0.0'),
    ('127.0.0.0', '255.0.0.0')
]

def is_private_ip(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_reserved
    except Exception:
        return False


def validate_url(url: str) -> bool:
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        return False
    if not p.netloc:
        return False
    # Prevent SSRF by disallowing private IPs as host
    host = p.hostname
    if host and is_private_ip(host):
        return False
    return True
