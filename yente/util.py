import codecs
from datetime import datetime
from prefixdate.precision import Precision
from typing import Any, List, Optional, Tuple

from yente import settings


class EntityRedirect(Exception):
    def __init__(self, canonical_id):
        self.canonical_id = canonical_id


class AsyncTextReaderWrapper:
    # from: https://github.com/MKuranowski/aiocsv/issues/2#issuecomment-706554973
    def __init__(self, obj, encoding, errors="strict"):
        self.obj = obj

        decoder_factory = codecs.getincrementaldecoder(encoding)
        self.decoder = decoder_factory(errors)

    async def read(self, size):
        raw_data = await self.obj.read(size)

        if not raw_data:
            return self.decoder.decode(b"", final=True)

        return self.decoder.decode(raw_data, final=False)


def match_prefix(prefix: str, *labels: Optional[str]):
    prefix = prefix.lower().strip()
    if not len(prefix):
        return False
    for label in labels:
        if label is None:
            continue
        label = label.lower().strip()
        if label.startswith(prefix):
            return True
    return False


def limit_window(limit: Any, offset: Any, default_limit: int = 10) -> Tuple[int, int]:
    """ElasticSearch can only return results from within a window of the first 10,000
    scored results. This means that offset + limit may never exceed 10,000 - so here's
    a bunch of bounding magic to enforce that."""
    try:
        num_limit = max(0, int(limit))
    except (ValueError, TypeError):
        num_limit = default_limit
    try:
        num_offset = max(0, int(offset))
        num_offset = min(settings.MAX_RESULTS, num_offset)
    except (ValueError, TypeError):
        num_offset = 0
    end = num_limit + num_offset
    if end > settings.MAX_RESULTS:
        num_limit = max(0, settings.MAX_RESULTS - num_offset)
    return num_limit, num_offset


def iso_datetime(value: str) -> datetime:
    """Parse a second-precision ISO date time string."""
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")


def expand_dates(dates: List[str]):
    """Expand a date into less precise versions of itself."""
    expanded = set(dates)
    for date in dates:
        for prec in (Precision.DAY, Precision.MONTH, Precision.YEAR):
            if len(date) > prec.value:
                expanded.add(date[: prec.value])
    return list(expanded)
