"""
Phase 17 – Security Sanitizer and Isolation Guards.
Blueprint Sections: 41-43, 55-58.

Implements:
1. Export formula safety: Sanitizes CSV/spreadsheet cells starting with formula injection triggers (=, +, -, @, \\t, \\r).
2. Log and payload redaction: Redacts passwords, tokens, JWTs, and secret keys.
3. Territory and role isolation guards.
4. Offline compliance verifier: Asserts no outbound network or cloud dependencies.
"""
import re
from typing import Any, Dict, List, Optional, Set, Union


# Characters that trigger formula execution in spreadsheet software (Excel, LibreOffice, Google Sheets)
FORMULA_TRIGGERS: Set[str] = {"=", "+", "-", "@", "\t", "\r"}


def sanitize_csv_cell(value: Any) -> str:
    """
    Sanitizes a single cell value to prevent CSV / Formula Injection attacks (CWE-1236).
    If a string starts with a formula trigger (=, +, -, @, \\t, \\r), it is prepended with a single quote (').
    """
    if value is None:
        return ""

    str_val = str(value)
    if not str_val:
        return ""

    first_char = str_val[0]
    if first_char in FORMULA_TRIGGERS:
        # Prepend single quote to neutralize formula evaluation
        return f"'{str_val}"

    # Also handle strings where whitespace or quotes precede a formula trigger
    stripped = str_val.lstrip()
    if stripped and stripped[0] in FORMULA_TRIGGERS:
        return f"'{str_val}"

    return str_val


def sanitize_csv_row(row: List[Any]) -> List[str]:
    """Sanitizes an entire row of cells for formula safety."""
    return [sanitize_csv_cell(cell) for cell in row]


# Sensitive keys that must be redacted from logs and responses
SENSITIVE_KEYS_PATTERN = re.compile(
    r"(password|passwd|token|secret|authorization|auth_header|bearer|jwt|cookie|api_key|private_key)",
    re.IGNORECASE,
)


def redact_sensitive_data(obj: Any, depth: int = 0) -> Any:
    """
    Recursively redacts sensitive keys from dictionaries, lists, and string payloads.
    Prevents leaking credentials in audit logs, RFC 7807 problem details, and error messages.
    """
    if depth > 10:
        return "<MAX_DEPTH_EXCEEDED>"

    if isinstance(obj, dict):
        redacted: Dict[str, Any] = {}
        for key, value in obj.items():
            if SENSITIVE_KEYS_PATTERN.search(str(key)):
                redacted[key] = "[REDACTED_CREDENTIAL]"
            else:
                redacted[key] = redact_sensitive_data(value, depth + 1)
        return redacted

    if isinstance(obj, list):
        return [redact_sensitive_data(item, depth + 1) for item in obj]

    if isinstance(obj, tuple):
        return tuple(redact_sensitive_data(item, depth + 1) for item in obj)

    if isinstance(obj, str):
        # Redact JWT tokens if detected in strings
        if len(obj) > 30 and obj.count(".") == 2 and obj.startswith("eyJ"):
            return "[REDACTED_JWT_TOKEN]"
        return obj

    return obj


class TerritoryIsolationGuard:
    """
    Validates cross-territory operations to ensure users cannot view or mutate
    corridors outside their authorized territorial boundaries.
    """

    @staticmethod
    def is_territory_allowed(user_territory: Optional[str], requested_territory: str) -> bool:
        """
        Returns True if user territory permits access to requested territory.
        None territory represents HQ / All-Territory jurisdiction.
        """
        if not requested_territory:
            return False

        if user_territory is None:
            # HQ / General jurisdiction
            return True

        return user_territory.strip().upper() == requested_territory.strip().upper()


class OfflineIntegrityVerifier:
    """
    Verifies that SAMARATH execution operates 100% offline without external CDN,
    analytics, or cloud AI API dependencies.
    """

    SUSPICIOUS_REMOTE_PATTERNS = [
        re.compile(r"https?://(api\.openai\.com|api\.anthropic\.com|generativelanguage\.googleapis\.com)"),
        re.compile(r"https?://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|unpkg\.com)"),
        re.compile(r"https?://(google-analytics\.com|segment\.io|mixpanel\.com)"),
    ]

    @classmethod
    def verify_no_external_endpoints(cls, payload_or_code: str) -> bool:
        """Returns True if no external API/CDN/Analytics domains are detected in payload."""
        for pattern in cls.SUSPICIOUS_REMOTE_PATTERNS:
            if pattern.search(payload_or_code):
                return False
        return True
