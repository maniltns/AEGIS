"""
AEGIS PII Scrubber
Uses Microsoft Presidio to sanitize PII before LLM processing.
"""

import logging
from typing import Optional

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False

logger = logging.getLogger("aegis.pii")

# Initialize engines globally (expensive to create)
_analyzer: Optional[AnalyzerEngine] = None
_anonymizer: Optional[AnonymizerEngine] = None


def _get_engines():
    """Lazy initialization of Presidio engines."""
    global _analyzer, _anonymizer
    
    if not PRESIDIO_AVAILABLE:
        logger.warning("Presidio not installed - PII scrubbing disabled")
        return None, None
    
    if _analyzer is None:
        _analyzer = AnalyzerEngine()
        _anonymizer = AnonymizerEngine()
    
    return _analyzer, _anonymizer


# PII types to detect and anonymize
PII_ENTITIES = [
    "PERSON",           # Names
    "EMAIL_ADDRESS",    # Emails
    "PHONE_NUMBER",     # Phone numbers
    "CREDIT_CARD",      # Credit cards
    "IBAN_CODE",        # Bank accounts
    "IP_ADDRESS",       # IPs
    "LOCATION",         # Addresses
    "DATE_TIME",        # Dates (optional)
    "NRP",              # National ID numbers
    "MEDICAL_LICENSE",  # Medical IDs
    "URL",              # URLs (optional)
]

# Replacement operators
OPERATORS = {
    "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
    "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE>"}),
    "CREDIT_CARD": OperatorConfig("replace", {"new_value": "<CARD>"}),
    "IBAN_CODE": OperatorConfig("replace", {"new_value": "<IBAN>"}),
    "IP_ADDRESS": OperatorConfig("replace", {"new_value": "<IP>"}),
    "LOCATION": OperatorConfig("replace", {"new_value": "<LOCATION>"}),
    "NRP": OperatorConfig("replace", {"new_value": "<ID>"}),
    "MEDICAL_LICENSE": OperatorConfig("replace", {"new_value": "<MEDICAL_ID>"}),
    "URL": OperatorConfig("replace", {"new_value": "<URL>"}),
    "DATE_TIME": OperatorConfig("keep"),  # Keep dates for context
}


def scrub_text(text: str, language: str = "en") -> str:
    """
    Scrub PII from text using Presidio.
    
    Args:
        text: Input text that may contain PII
        language: Language code (default: "en")
        
    Returns:
        Anonymized text with PII replaced by placeholders
    """
    if not text or not text.strip():
        return text
    
    analyzer, anonymizer = _get_engines()
    
    if analyzer is None:
        # Fallback: basic regex-based scrubbing
        return _fallback_scrub(text)
    
    try:
        # Analyze text for PII
        results = analyzer.analyze(
            text=text,
            entities=PII_ENTITIES,
            language=language
        )
        
        if not results:
            return text
        
        # Anonymize detected PII
        anonymized = anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=OPERATORS
        )
        
        logger.debug(f"Scrubbed {len(results)} PII entities")
        return anonymized.text
        
    except Exception as e:
        logger.error(f"PII scrubbing failed: {e}")
        return _fallback_scrub(text)


def _fallback_scrub(text: str) -> str:
    """
    Fallback regex-based scrubbing when Presidio is unavailable.
    Less accurate but provides basic protection.
    """
    import re
    
    # Email pattern
    text = re.sub(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        '<EMAIL>',
        text
    )
    
    # Phone patterns (various formats)
    text = re.sub(
        r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        '<PHONE>',
        text
    )
    
    # Credit card patterns (basic)
    text = re.sub(
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        '<CARD>',
        text
    )
    
    # IP addresses
    text = re.sub(
        r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        '<IP>',
        text
    )
    
    # SSN patterns (US)
    text = re.sub(
        r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
        '<SSN>',
        text
    )
    
    return text


def scrub_incident(text: str) -> str:
    """
    Convenience wrapper for incident description scrubbing.
    
    Args:
        text: Incident description text
        
    Returns:
        Scrubbed text safe for LLM processing
    """
    return scrub_text(text, language="en")


def scrub_dict(data: dict, fields: list = None) -> dict:
    """
    Scrub PII from specified fields in a dictionary.
    
    Args:
        data: Dictionary containing incident data
        fields: List of field names to scrub (default: description fields)
        
    Returns:
        Dictionary with scrubbed fields
    """
    if fields is None:
        fields = ["short_description", "description", "comments", "work_notes"]
    
    scrubbed = data.copy()
    
    for field in fields:
        if field in scrubbed and isinstance(scrubbed[field], str):
            scrubbed[field] = scrub_text(scrubbed[field])
    
    return scrubbed


# Quick test
if __name__ == "__main__":
    test_cases = [
        "Call me at 555-123-4567 or email john.doe@accor.com",
        "My credit card is 4111-1111-1111-1111",
        "Server IP is 192.168.1.100 and user is Jane Smith",
        "SSN: 123-45-6789",
    ]
    
    print("PII Scrubber Test:")
    print("=" * 50)
    
    for test in test_cases:
        result = scrub_text(test)
        print(f"IN:  {test}")
        print(f"OUT: {result}")
        print()
