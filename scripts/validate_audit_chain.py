from algo_tf.audit.chain import append_event

if __name__ == "__main__":
    chain = []
    append_event(chain, {"event": 1})
    append_event(chain, {"event": 2})
    assert chain[1].previous_hash == chain[0].event_hash
    print("audit_chain_valid")
