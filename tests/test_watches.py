from datetime import datetime,timedelta,timezone
import pytest
from backend.watches import draft,evaluate,preview
from backend.numbers import daily_signal,IST
from backend.network import SourceError


def bars():
    start=datetime(2026,1,1,9,15,tzinfo=IST)
    return {'timestamp':[int((start+timedelta(days=i)).timestamp()) for i in range(55)],
            'indicators':{'quote':[{'close':[100]*54+[110],'volume':[100]*54+[200]}]}}


def test_sentence_grammar_preserves_equality_and_refuses_extra_conditions():
    assert draft('Alert me when TCS falls more than 5%')['operator']=='gt'
    assert draft('TCS volume is at least 2x usual')['operator']=='gte'
    for text in ['TCS falls more than 5% and margins weaken','Buy TCS below 3000','TCS falls 5','TCS fires missiles']:
        with pytest.raises(SourceError):draft(text)


def test_threshold_uses_exact_inputs_not_rounded_display():
    rule=draft('TCS volume is more than 2x usual')
    signal={'volume_multiple':2,'operands':{'current_volume':'200001','average_previous_20_volume':'100000'}}
    assert evaluate(rule,signal)
    signal['operands']['current_volume']='200000'
    assert evaluate(rule,signal) is False
    assert evaluate({**rule,'operator':'gte'},signal)


def test_preview_excludes_future_data_and_missing_baseline_cannot_be_skipped():
    c=bars();rule=draft('TCS volume is at least 2x usual')
    result=preview(rule,c)
    assert result['eligible_sessions']==30 and len(result['firings'])==1
    before=daily_signal(c,datetime(2026,2,23,16,tzinfo=IST))
    assert before['volume_multiple']==1
    c['indicators']['quote'][0]['volume'][-3]=None
    latest=daily_signal(c,datetime(2026,4,1,tzinfo=timezone.utc))
    assert latest['volume_multiple'] is None
    assert evaluate(rule,latest) is None
