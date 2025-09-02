import re
from typing import List, Tuple, Any
from src.utils.logging import get_logger
logger = get_logger("mask")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\d{3}[-.\s]?){2}\d{4}\b")

def mask_value(v: Any) -> Any:
    if not isinstance(v, str):
        return v
    original_v = v
    v = EMAIL_RE.sub("[EMAIL_MASKED]", v)
    v = PHONE_RE.sub("[PHONE_MASKED]", v)
    if original_v != v:
        logger.debug(f"Masked value: '{original_v}' -> '{v}'")
    return v

def mask_results(columns: List[str], rows: List[Tuple[Any, ...]]) -> List[Tuple[Any, ...]]:
    sensitive_names = {"email", "phone", "ssn", "credit_card", "pan", "aadhaar", "password"}
    col_lower = [c.lower() for c in columns]
    sensitive_idx = [i for i, c in enumerate(col_lower) if any(s in c for s in sensitive_names)]
    logger.info(f"Sensitive columns detected at indices: {sensitive_idx}")
    masked = []
    for row_num, r in enumerate(rows):
        r_list = list(r)
        for i in sensitive_idx:
            if i < len(r_list):
                logger.debug(f"Row {row_num}: Masking sensitive column '{columns[i]}' value '{r_list[i]}'")
                r_list[i] = "[MASKED]"
        # Regex-level masking for free-text columns
        r_list_masked = [mask_value(v) for v in r_list]
        masked.append(tuple(r_list_masked))
    logger.info(f"Total rows masked: {len(masked)}")
    return masked
