from typing import Optional
from datetime import datetime


def match_prefix(prefix: str, *labels: Optional[str]):
    prefix = prefix.lower().strip()
    if not len(prefix):
        return True
    for label in labels:
        if label is None:
            continue
        label = label.lower().strip()
        if label.startswith(prefix):
            return True
    return False


def iso_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")