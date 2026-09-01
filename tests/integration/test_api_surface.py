from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from algo_tf.app import app
from algo_tf.settings import settings


def test_required_endpoints_exist_and_no_order_verb_endpoints() -> None:
    client = TestClient(app)
    openapi = client.get('/openapi.json').json()
    paths = set(openapi['paths'].keys())

    required = {
        '/health',
        '/ready',
        '/mandates',
        '/mandates/{mandate_id}/arm',
        '/mandates/{mandate_id}/pause',
        '/mandates/{mandate_id}/revoke',
        '/mandates/{mandate_id}',
        '/mandates/{mandate_id}/state',
        '/observations/quote',
        '/observations/gex',
        '/observations/greeks',
        '/observations/position',
        '/eligibility-updates',
        '/execution-updates',
        '/decisions/{decision_id}',
        '/mandates/{mandate_id}/decisions',
        '/mandates/{mandate_id}/intents',
        '/kill-switch/activate',
        '/kill-switch/status',
        '/audit/events',
    }
    assert required.issubset(paths)
    assert '/buy' not in paths
    assert '/sell' not in paths
    assert '/place_order' not in paths
    assert '/trade' not in paths


def test_mandate_ingest_and_arm_flow() -> None:
    client = TestClient(app)
    headers = {'x-api-key': settings.api_key}
    now = datetime.now(UTC)
    payload = {
        'mandate_id': 'm-int-1',
        'strategy_id': 's1',
        'strategy_version': 1,
        'sleeve_element_id': 'el1',
        'instrument': 'QQQ',
        'asset_class': 'ETF',
        'direction': 'LONG',
        'maximum_notional': 100000,
        'maximum_loss': 1000,
        'maximum_slippage_bps': 20,
        'allowed_actions': ['ENTER', 'SCALE_IN'],
        'maximum_child_orders': 5,
        'maximum_reentries': 1,
        'maximum_state_flips': 2,
        'permitted_order_types': ['LIMIT'],
        'effective_at': (now - timedelta(minutes=1)).isoformat(),
        'expires_at': (now + timedelta(minutes=10)).isoformat(),
    }

    ingest = client.post('/mandates', json=payload, headers=headers)
    assert ingest.status_code == 200
    arm = client.post('/mandates/m-int-1/arm', headers=headers)
    assert arm.status_code == 200
    state = client.get('/mandates/m-int-1/state', headers=headers)
    assert state.json()['state'] == 'ARMED'
