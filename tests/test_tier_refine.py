from backend.brief import refine_tier

BOARD='Board or senior-management change; review the terms.'


def ev(**k):
    return {'kind':'filing','tier':0,'assessment':'assessed','title':'Appointment','reason':BOARD,**k}


def test_director_reappointment_moves_to_worth_knowing_with_reason_kept():
    e=refine_tier(ev(trigger_quote='The Board approved the re-appointment of Ms. A as an Independent Director.'))
    assert e['tier']==1 and 'Moved from Needs you' in e['tier_note']


def test_senior_exits_and_material_items_stay_in_needs_you():
    assert refine_tier(ev(trigger_quote='Mr. B has resigned as Chief Financial Officer.'))['tier']==0
    assert refine_tier(ev(trigger_quote='Appointment of Mr. C as Managing Director and CEO.'))['tier']==0
    assert refine_tier(ev(reason='Financial results disclosed; review performance and basis.'))['tier']==0
    assert refine_tier(ev(reason='Auditor or audit concern; inspect the disclosure.'))['tier']==0


def test_routine_auditor_newspaper_and_generic_pending_titles_are_demoted():
    assert refine_tier(ev(reason='Auditor appointment or reappointment disclosed; inspect the terms.'))['tier']==1
    assert refine_tier(ev(reason='Newspaper attachment needs issuer-specific labels.'))['tier']==1
    assert refine_tier(ev(assessment='pending',reason='Potentially important exchange notice.',description='Outcome of Board Meeting · x'))['tier']==1
    assert refine_tier({'kind':'price','tier':0,'reason':BOARD})['tier']==0
