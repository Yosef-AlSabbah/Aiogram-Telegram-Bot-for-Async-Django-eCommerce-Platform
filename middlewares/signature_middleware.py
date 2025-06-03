"""
Single aiohttp middleware that automatically signs ONLY backend requests
Ignores Telegram API and other external requests
"""
import aiohttp
import hmac
import hashlib
import time
import uuid
import json
import logging
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Store original methods
_original_request = aiohttp.ClientSession._request


class SignatureMiddleware:
    """
    Single middleware that automatically signs only specified backend requests
    """

    def __init__(self, secret_key: str,
                 backend_urls: Union[str, List[str]],
                 validity_window: int = 300,
                 signature_header: str = 'X-Signature',
                 timestamp_header: str = 'X-Timestamp',
                 nonce_header: str = 'X-Nonce',
                 debug: bool = False):
        """
        Initialize signature middleware

        Args:
            secret_key: Secret key for HMAC signing (same as Django)
            backend_urls: URL(s) to sign requests for. Can be:
                         - Single URL: "https://your-backend.com"
                         - List of URLs: ["https://api1.com", "https://api2.com"]
                         - Domain: "your-backend.com" (matches any protocol)
            validity_window: Signature validity in seconds (default: 300)
            signature_header: Header name for signature (default: X-Signature)
            timestamp_header: Header name for timestamp (default: X-Timestamp)
            nonce_header: Header name for nonce (default: X-Nonce)
            debug: Enable debug logging (default: False)
        """
        if not secret_key:
            raise ValueError("Secret key is required")
        if not backend_urls:
            raise ValueError("Backend URLs are required")

        self.secret_key = secret_key
        self.validity_window = validity_window
        self.signature_header = signature_header
        self.timestamp_header = timestamp_header
        self.nonce_header = nonce_header
        self.debug = debug

        # Normalize backend URLs to a list
        if isinstance(backend_urls, str):
            self.backend_urls = [backend_urls]
        else:
            self.backend_urls = list(backend_urls)

        # Prepare URL patterns for matching
        self.url_patterns = []
        for url in self.backend_urls:
            # Remove trailing slashes and store for matching
            clean_url = url.rstrip('/')
            self.url_patterns.append(clean_url)

        if self.debug:
            logger.info(f"🔐 SignatureMiddleware initialized")
            logger.info(f"   Backend URLs: {self.backend_urls}")
            logger.info(f"   Validity window: {validity_window}s")

    def install(self):
        """Install the middleware globally for ALL aiohttp sessions"""

        async def signed_request(session_self, method: str, url, **kwargs):
            """Replacement for aiohttp.ClientSession._request that adds signatures"""

            # Check if this URL should be signed
            if self._should_sign_request(str(url)):
                # Extract path from URL for signature
                parsed_url = urlparse(str(url))
                path = parsed_url.path or '/'

                # Get body for signature
                body = self._get_body_for_signature(kwargs)

                # Generate signature headers
                signature_headers = self._create_manual_signature(method, path, body)

                # Add signature headers to request
                headers = kwargs.get('headers', {})
                headers.update(signature_headers)
                kwargs['headers'] = headers

                if self.debug:
                    nonce_short = signature_headers[self.nonce_header][:8]
                    logger.debug(f"🔐 Auto-signing {method} {path} (nonce: {nonce_short}...)")
            else:
                if self.debug:
                    parsed_url = urlparse(str(url))
                    logger.debug(f"⏭️  Skipping signature for {method} {parsed_url.netloc}{parsed_url.path}")

            # Call original request method
            return await _original_request(session_self, method, url, **kwargs)

        # Monkey patch aiohttp.ClientSession._request
        aiohttp.ClientSession._request = signed_request

        if self.debug:
            logger.info("✅ SignatureMiddleware installed globally")

    def uninstall(self):
        """Restore original aiohttp behavior"""
        aiohttp.ClientSession._request = _original_request

        if self.debug:
            logger.info("❌ SignatureMiddleware uninstalled")

    def _should_sign_request(self, url: str) -> bool:
        """Check if this URL should be signed"""
        parsed_url = urlparse(url)
        request_host = parsed_url.netloc.lower()
        request_url = f"{parsed_url.scheme}://{request_host}".rstrip('/')

        # Skip Telegram API requests
        if 'api.telegram.org' in request_host:
            return False

        # Check against our backend URLs
        for pattern in self.url_patterns:
            pattern_lower = pattern.lower()

            # If pattern is just a domain (no protocol)
            if not pattern_lower.startswith(('http://', 'https://')):
                if pattern_lower in request_host:
                    return True
            else:
                # Full URL matching
                if request_url.startswith(pattern_lower):
                    return True

                # Also check if just the domain matches
                pattern_parsed = urlparse(pattern_lower)
                if pattern_parsed.netloc in request_host:
                    return True

        return False

    def _get_body_for_signature(self, kwargs) -> Any:
        """Extract body from request kwargs"""
        if 'json' in kwargs:
            return kwargs['json']
        elif 'data' in kwargs:
            return kwargs['data']
        return None

    def _create_manual_signature(self, method: str, path: str, body: Any = None,
                                timestamp: int = None, nonce: str = None) -> Dict[str, str]:
        """
        Create signature headers - exactly matches your Django create_manual_signature function
        """
        if timestamp is None:
            timestamp = int(time.time())

        if nonce is None:
            nonce = str(uuid.uuid4())

        # Normalize body - exactly matches Django implementation
        body_str = ""
        if body is not None:
            if isinstance(body, dict):
                body_str = json.dumps(body, separators=(',', ':'), sort_keys=True, ensure_ascii=True)
            elif isinstance(body, str):
                body_str = body
            else:
                body_str = str(body)

        # Create message - exactly matches Django format
        message = f"{method.upper()}|{path}|{body_str}|{timestamp}|{nonce}"

        # Calculate signature - exactly matches Django implementation
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return {
            self.signature_header: signature,
            self.timestamp_header: str(timestamp),
            self.nonce_header: nonce
        }


# Global middleware instance
_middleware_instance: Optional[SignatureMiddleware] = None


def install_signature_middleware(secret_key: str,
                               backend_urls: Union[str, List[str]],
                               validity_window: int = 300,
                               signature_header: str = 'X-Signature',
                               timestamp_header: str = 'X-Timestamp',
                               nonce_header: str = 'X-Nonce',
                               debug: bool = False):
    """
    Install signature middleware for specific backend URLs only

    Args:
        secret_key: Secret key for HMAC signing (same as Django)
        backend_urls: URL(s) to sign requests for. Examples:
                     - "https://your-backend.com"
                     - ["https://api1.com", "https://api2.com"]
                     - "your-backend.com" (domain only)
        validity_window: Signature validity in seconds (default: 300)
        signature_header: Header name for signature (default: X-Signature)
        timestamp_header: Header name for timestamp (default: X-Timestamp)
        nonce_header: Header name for nonce (default: X-Nonce)
        debug: Enable debug logging (default: False)
    """
    global _middleware_instance

    if _middleware_instance:
        logger.warning("Signature middleware already installed. Uninstalling previous instance.")
        _middleware_instance.uninstall()

    _middleware_instance = SignatureMiddleware(
        secret_key=secret_key,
        backend_urls=backend_urls,
        validity_window=validity_window,
        signature_header=signature_header,
        timestamp_header=timestamp_header,
        nonce_header=nonce_header,
        debug=debug
    )

    _middleware_instance.install()
    return _middleware_instance


def uninstall_signature_middleware():
    """Uninstall signature middleware and restore original aiohttp behavior"""
    global _middleware_instance

    if _middleware_instance:
        _middleware_instance.uninstall()
        _middleware_instance = None
        logger.info("✅ Signature middleware uninstalled")
    else:
        logger.warning("No signature middleware installed")


def is_middleware_installed() -> bool:
    """Check if signature middleware is currently installed"""
    return _middleware_instance is not None