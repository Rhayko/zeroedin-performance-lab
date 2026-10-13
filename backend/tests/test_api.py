def athlete(client):
    r=client.post('/api/athletes',json={'name':'Test Athlete','sport':'Track'})
    assert r.status_code == 201
    return r.json()['id']

def test_health(client):
    assert client.get('/health').json() == {'status':'ok'}

def test_demo_seed_is_idempotent(client):
    first=client.post('/api/demo/seed')
    second=client.post('/api/demo/seed')
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()['id'] == second.json()['id']
    assert len(client.get('/api/athletes').json()) == 1

def test_checkin_and_analytics(client):
    aid=athlete(client)
    body={'recorded_date':'2025-01-01','fatigue':2,'stress':2,'motivation':4,'perceived_recovery':4,'sleep':{'duration_hours':8,'quality':4},'symptoms':[]}
    assert client.post(f'/api/athletes/{aid}/daily-states',json=body).status_code == 201
    assert client.post(f'/api/athletes/{aid}/daily-states',json=body).status_code == 409
    data=client.get(f'/api/athletes/{aid}/analytics').json()
    assert data['baseline']['message'] == 'Baseline building: Day 1/28'
    assert data['scope_note'].startswith('All current analytics are descriptive')

def test_session_sets_and_prediction_guard(client):
    aid=athlete(client)
    body={'performed_at':'2025-01-01T10:00:00','session_type':'Strength','duration_minutes':60,'session_rpe':7,'sets':[{'exercise_name':'Squat','set_number':1,'reps':5,'load_kg':100,'rpe':8,'rir':2}]}
    result=client.post(f'/api/athletes/{aid}/sessions',json=body)
    assert result.status_code == 201
    assert result.json()['sets'][0]['load_kg'] == 100
    prediction={'target':'CMJ','predicted_value':40,'unit':'cm','model_version':'test','target_date':'2025-01-02T10:00:00'}
    guarded=client.post(f'/api/athletes/{aid}/predictions',json=prediction)
    assert guarded.status_code == 403

def test_profile_update_and_record_corrections(client):
    aid=athlete(client)
    updated=client.patch(f'/api/athletes/{aid}',json={'sport':'Tactical performance','goals':'Improve loaded movement capacity'})
    assert updated.status_code == 200
    assert updated.json()['sport'] == 'Tactical performance'

    state={'recorded_date':'2025-02-01','fatigue':3,'stress':3,'motivation':4,'perceived_recovery':3,'sleep':{'duration_hours':7,'quality':3},'symptoms':[]}
    state_id=client.post(f'/api/athletes/{aid}/daily-states',json=state).json()['id']
    assert client.delete(f'/api/athletes/{aid}/daily-states/{state_id}').status_code == 204
    assert client.delete(f'/api/athletes/{aid}/daily-states/{state_id}').status_code == 404

    session={'performed_at':'2025-02-01T06:00:00','session_type':'Load carriage / ruck','duration_minutes':90,'session_rpe':7,'sets':[]}
    session_id=client.post(f'/api/athletes/{aid}/sessions',json=session).json()['id']
    assert client.delete(f'/api/athletes/{aid}/sessions/{session_id}').status_code == 204

    test={'performed_at':'2025-02-02T06:00:00','test_type':'Loaded march / ruck','value':65,'unit':'min'}
    test_id=client.post(f'/api/athletes/{aid}/performance-tests',json=test).json()['id']
    assert client.delete(f'/api/athletes/{aid}/performance-tests/{test_id}').status_code == 204

def test_local_exports(client):
    aid=athlete(client)
    backup=client.get(f'/api/athletes/{aid}/export.json')
    assert backup.status_code == 200
    assert backup.json()['format'] == 'zeroedin-local-backup-v1'
    assert backup.json()['athlete']['name'] == 'Test Athlete'
    assert 'attachment' in backup.headers['content-disposition']

    records=client.get(f'/api/athletes/{aid}/export.csv')
    assert records.status_code == 200
    assert records.text.startswith('record_type,date,category')
    assert records.headers['content-type'].startswith('text/csv')

    restored=client.post('/api/import',json=backup.json())
    assert restored.status_code == 201
    assert restored.json()['name'] == 'Test Athlete'
    assert restored.json()['id'] != aid

    invalid=client.post('/api/import',json={'format':'unknown'})
    assert invalid.status_code == 400
