"""Financial arithmetic is deterministic; models never calculate these values."""
from decimal import Decimal,InvalidOperation
from datetime import datetime,timezone,timedelta

IST=timezone(timedelta(hours=5,minutes=30))

def decimal(value):
    if value is None:raise ValueError('Missing value')
    d=Decimal(str(value))
    if not d.is_finite():raise ValueError('Non-finite value')
    return d

def display(value,places=2):return float(value.quantize(Decimal(10)**-places))

def daily_signal(chart,at=None):
    at=at or datetime.now(timezone.utc)
    quote=chart['indicators']['quote'][0]; stamps=chart.get('timestamp',[])
    today=at.astimezone(IST).date(); bars=[]
    regular_end=chart.get('meta',{}).get('currentTradingPeriod',{}).get('regular',{}).get('end')
    for i,stamp in enumerate(stamps):
        session=datetime.fromtimestamp(stamp,IST)
        end=datetime.combine(session.date(),datetime.min.time(),IST)+timedelta(hours=15,minutes=30)
        if regular_end and datetime.fromtimestamp(regular_end,IST).date()==session.date():end=datetime.fromtimestamp(regular_end,IST)
        if session.date()>today or at<end:continue
        try:
            close=decimal(quote['close'][i])
            if close<=0:continue
        except (ValueError,InvalidOperation,IndexError,KeyError,TypeError):continue
        try:
            volume=decimal(quote['volume'][i])
            if volume<0:volume=None
        except (ValueError,InvalidOperation,IndexError,KeyError,TypeError):volume=None
        bars.append({'time':stamp,'date':session.date().isoformat(),'close':close,'volume':volume})
    if not bars:return {'status':'unavailable','reason':'No completed daily session was available.'}
    current=bars[-1];previous=bars[-2] if len(bars)>1 else None
    split_times=[int(x.get('date',k)) for k,x in chart.get('events',{}).get('splits',{}).items()]
    price_split=previous and any(previous['time']<s<=current['time'] for s in split_times)
    volume_bars=[b for b in bars[:-1] if b['volume'] is not None][-20:]
    volume_split=len(volume_bars)==20 and any(volume_bars[0]['time']<=s<=current['time'] for s in split_times)
    change=(current['close']/previous['close']-1)*100 if previous and not price_split else None
    baseline=sum(b['volume'] for b in volume_bars)/20 if len(volume_bars)==20 else None
    multiple=current['volume']/baseline if baseline and current['volume'] is not None and not volume_split else None
    reason='Corporate action crosses the comparison window.' if price_split or volume_split else 'At least 21 completed sessions are needed for volume comparison.' if baseline is None else 'Volume baseline is zero.' if baseline==0 else None
    return {'status':'available','session':current['date'],'close':display(current['close']),
        'change_percent':display(change) if change is not None else None,'volume':int(current['volume']) if current['volume'] is not None else None,
        'volume_multiple':display(multiple) if multiple is not None else None,'comparison_limit':reason,
        'operands':{'current_close':str(current['close']),'previous_close':str(previous['close']) if previous else None,
            'previous_session':previous['date'] if previous else None,'current_volume':str(current['volume']),
            'previous_20_volumes':[str(b['volume']) for b in volume_bars] if baseline is not None else [],
            'average_previous_20_volume':str(baseline) if baseline is not None else None},
        'formula':'Change = 100 × (latest completed Close / previous completed Close − 1). Volume = latest volume / mean of the preceding 20 completed sessions. Current session excluded from baseline.',
        'price_basis':'Yahoo daily Close, not dividend-adjusted Close','currency':chart.get('meta',{}).get('currency','INR')}

UNITS={'rupee':Decimal(1),'lakh':Decimal(100000),'crore':Decimal(10000000),'million':Decimal(1000000),'billion':Decimal(1000000000)}

def comparable_growth(current,prior):
    """Only caller-verified narrative operands; ambiguous PDF table columns are not inputs."""
    for field in ('metric','currency','scope','period_kind'):
        if not current.get(field) or current[field]!=prior.get(field):raise ValueError('Incompatible '+field)
    for operand in (current,prior):
        for field in ('period_start','period_end','evidence_id','quote','unit'):
            if not operand.get(field):raise ValueError('Missing source operand '+field)
        if operand['unit'] not in UNITS:raise ValueError('Unknown unit')
    a=decimal(current['value'])*UNITS[current['unit']];b=decimal(prior['value'])*UNITS[prior['unit']]
    if b<=0:raise ValueError('Growth from a zero or negative base is not reported as a percentage')
    if current['period_start']<=prior['period_start']:raise ValueError('Periods are not in chronological order')
    ca=datetime.fromisoformat(current['period_end'])-datetime.fromisoformat(current['period_start'])
    cb=datetime.fromisoformat(prior['period_end'])-datetime.fromisoformat(prior['period_start'])
    if abs((ca-cb).days)>2:raise ValueError('Period lengths differ')
    return (a/b-1)*100

