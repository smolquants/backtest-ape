def test_calls(setter, acc, alice, bob):
    # set owner to alice then bob
    datas = [
        setter.set.as_transaction(alice.address).data,
        setter.set.as_transaction(bob.address).data,
    ]

    # internal calls alice then bob as owner through setter
    receipt = setter.calls(datas, sender=acc)

    # check bob now owner
    assert setter.owner() == bob.address

    # check via events that alice had been owner
    logs = [log for log in setter.Set.from_receipt(receipt)]
    assert len(logs) == 2
    assert logs[0]._owner == alice.address
    assert logs[1]._owner == bob.address
