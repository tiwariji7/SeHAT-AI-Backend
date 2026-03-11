import logging
import os
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def extract_numeric(value_str: str) -> Optional[float]:
    """
    Extract the first numeric value from a string such as '11.2 g/dL' or '140 mg/dL'.

    Returns:
        The numeric value as a float, or None if no number is found.
    """
    match = re.search(r"[-+]?\d*\.?\d+", str(value_str))
    return float(match.group()) if match else None


def parse_reference_range(ref_str: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse a reference range string into (low, high) float bounds.

    Supported formats:
      - "13-17"  or  "13 - 17"    →  (13.0, 17.0)
      - "70 to 110"               →  (70.0, 110.0)
      - "<200"                    →  (None, 200.0)
      - ">40"                     →  (40.0, None)

    Returns:
        Tuple of (low, high); None means the bound is open/unbounded.
    """
    ref_str = str(ref_str).strip()

    # Range: "13-17", "13 – 17", "70 to 110"
    range_match = re.match(
        r"^([\d.]+)\s*(?:[-–—]|to)\s*([\d.]+)$", ref_str, re.IGNORECASE
    )
    if range_match:
        return float(range_match.group(1)), float(range_match.group(2))

    # Upper bound only: "<200"
    lt_match = re.match(r"^<\s*([\d.]+)$", ref_str)
    if lt_match:
        return None, float(lt_match.group(1))

    # Lower bound only: ">40"
    gt_match = re.match(r"^>\s*([\d.]+)$", ref_str)
    if gt_match:
        return float(gt_match.group(1)), None

    logger.warning("Could not parse reference range: '%s'", ref_str)
    return None, None


def detect_abnormal_parameters(parameters: list) -> list:
    """
    Compare each lab parameter against its reference range.

    Args:
        parameters: List of LabParameter Pydantic objects with
                    .name, .value (str), and .references (str) attributes.

    Returns:
        List of dicts for abnormal parameters only, each with keys:
        name, value (float), status ('Low' or 'High'), reference (str).
    """
    abnormal = []

    for param in parameters:
        numeric_value = extract_numeric(param.value)
        if numeric_value is None:
            logger.warning(
                "Skipping '%s': could not extract numeric value from '%s'",
                param.name,
                param.value,
            )
            continue

        low, high = parse_reference_range(param.references)

        status: Optional[str] = None
        if low is not None and numeric_value < low:
            status = "Low"
        elif high is not None and numeric_value > high:
            status = "High"

        if status:
            abnormal.append(
                {
                    "name": param.name,
                    "value": numeric_value,
                    "status": status,
                    "reference": param.references,
                }
            )

    return abnormal


def build_abnormal_summary(abnormal_params: list) -> str:
    """
    Build a human-readable text block listing all abnormal parameters.
    Used as context for the LLM prompt.
    """
    lines = [
        f"{p['name']} : {p['value']} ({p['status']}) | Reference: {p['reference']}"
        for p in abnormal_params
    ]
    return "\n".join(lines)
