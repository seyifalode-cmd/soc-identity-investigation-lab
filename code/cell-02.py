for label, (rows, expected) in tests.items():
    actual = len(detect(rows))
    assert actual == expected, (label, actual, expected)
    print(f"PASS | {label}: {actual} alert(s)")
print("10 checks passed. A matching pattern still needs investigation.")
