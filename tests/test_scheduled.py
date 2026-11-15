from datetime import datetime,timezone
import pytest
from fastapi.testclient import TestClient
from backend import repository,store,scheduled,work
from backend.main import app

@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):
    monkeypatch.setattr(repository,'DATA',tmp_path);monkeypatch.setattr(store,'DATA',tmp_path)
    repository.init();store.init()

def test_scheduler_disabled_by_default_and_bearer_scoped(monkeypatch):
    monkeypatch.delenv('FINN_SCHEDULER_ENABLED',raising=False)
    with TestClient(app) as client:
        assert client.post('/api/internal/schedule').status_code!=200
        monkeypatch.setenv('FINN_SCHEDULER_ENABLED','true');monkeypatch.setenv('FINN_SCHEDULER_TOKEN','x'*40)
        assert client.post('/api/internal/schedule').status_code==401
        assert client.post('/api/internal/schedule',headers={'Authorization':'Bearer wrong'}).status_code==401
        first=client.post('/api/internal/schedule',headers={'Authorization':'Bearer '+'x'*40}).json()
        again=client.post('/api/internal/schedule',headers={'Authorization':'Bearer '+'x'*40}).json()
        assert first['id']==again['id']
        assert client.get('/api/jobs/'+first['id']).status_code==410
        assert client.get('/api/internal/schedule/'+first['id']).status_code==401

def test_completed_schedule_slot_never_enqueues_duplicate_work():
    first=scheduled.submit(datetime(2026,11,15,3,tzinfo=timezone.utc))
    job=work.claim();work.finish(job,{'status':'complete','stage':'Complete'})
    again=scheduled.submit(datetime(2026,11,15,4,tzinfo=timezone.utc))
    assert first['id']==again['id'] and again['status']=='complete'
    evening=scheduled.submit(datetime(2026,11,15,10,tzinfo=timezone.utc))
    assert evening['id']!=first['id']


def test_reminder_uses_new_notice_without_silently_moving_users_date():
    event={'event_id':'original','symbol':'TCS','date':'2026-11-20','kind':'call','status':'scheduled'}
    repository.save('alice','reminders','r',{'event':event,'enabled':True})
    revised={**event,'event_id':'new-notice','status':'cancelled','replacement_date':'2026-11-23'}
    store.put('brief-snapshot',{'events':[{'published_at':'2026-11-17','upcoming_dates':[revised]}]})
    scheduled.reminders('alice',datetime(2026,11,18,tzinfo=timezone.utc))
    status=repository.get('alice','reminder_status','r')
    assert status['status']=='rescheduled_review_required' and status['latest_notice']['replacement_date']=='2026-11-23'
    assert repository.get('alice','reminders','r')['event']['date']=='2026-11-20'
    store.put('brief-snapshot',{'events':[]})
    scheduled.reminders('alice',datetime(2026,11,21,tzinfo=timezone.utc))
    assert repository.get('alice','reminder_status','r')['status']=='past_date_not_delivered'
    assert repository.get('bob','reminder_status','r') is None


# Regression: adversarial review F12. A disabled scheduler answered 503, which the
# workflow treats as transient and retries for 27 minutes.
def test_disabled_scheduler_is_not_reported_as_a_transient_outage(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    monkeypatch.setenv('FINN_SCHEDULER_ENABLED','false')
    with TestClient(app) as client:
        assert client.post('/api/internal/schedule',headers={'Authorization':'Bearer '+'x'*40}).status_code==404
