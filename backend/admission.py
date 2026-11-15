"""Durable, atomic free-quota admission shared by web and scheduled workers."""
import time
from . import repository
from .network import SourceError


def reserve(key,tokens,baseline=None,at=None):
    stamp=time.time() if at is None else at
    baseline=baseline or {'reserved_tokens':0,'requests':0}
    for attempt in range(8):
        current=repository.get('_system','admission',key) or {'reserved_tokens':0,'requests':0,'next_allowed':0,'_version':0}
        reserved=max(current['reserved_tokens'],baseline['reserved_tokens'])
        requests=max(current['requests'],baseline['requests'])
        if reserved+tokens>180000 or requests>=900:
            raise SourceError('daily_quota','FINN has reached its conservative daily free allowance. Stored sources remain readable.')
        if current.get('next_allowed',0)>stamp:
            raise SourceError('quota_wait','Shared answer capacity is reserved. Retry after the current minute; stored evidence remains readable.')
        try:
            return repository.save('_system','admission',key,{'reserved_tokens':reserved+tokens,
                'requests':requests+1,'next_allowed':stamp+61},expected=current['_version'])
        except repository.Conflict:
            if attempt==7:raise SourceError('busy','Shared answer capacity is busy. Retry shortly.') from None
