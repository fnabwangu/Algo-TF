from pathlib import Path


def test_no_direct_broker_sdk_or_robinhood_url() -> None:
    root = Path(__file__).resolve().parents[2] / "algo_tf"
    forbidden = ("robinhood", "brokerapi", "api.robinhood")
    for path in root.rglob('*.py'):
        content = path.read_text(encoding='utf-8').lower()
        assert all(term not in content for term in forbidden), f"forbidden term found in {path}"


def test_only_execution_engine_adapter_mentions_submit_intent_boundary() -> None:
    root = Path(__file__).resolve().parents[2] / "algo_tf"
    expected = root / 'adapters' / 'execution' / 'execution_engine_client.py'
    offenders: list[Path] = []
    for path in root.rglob('*.py'):
        content = path.read_text(encoding='utf-8')
        if 'submit_intent(' in content and path != expected:
            offenders.append(path)
    assert offenders == []
