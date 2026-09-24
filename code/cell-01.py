from datetime import datetime, timedelta, timezone
import json, time, threading, queue, secrets, hashlib, hmac
from pathlib import Path

BASE = datetime(2026, 9, 23, 9, 0, tzinfo=timezone.utc)


def event(i, seconds, result, user="alex", ip="192.0.2.10"):
    return dict(
        id=i,
        time=BASE + timedelta(seconds=seconds),
        user=user,
        ip=ip,
        app="DeliveryPortal",
        result=result,
    )


def detect(events):
    unique = {e["id"]: e for e in events}
    rows = sorted(unique.values(), key=lambda e: (e["time"], e["id"]))
    alerts = []
    for success in rows:
        if success["result"] != "Success":
            continue
        failures = [
            e
            for e in rows
            if e["result"] == "Failed"
            and all(e[k] == success[k] for k in ("user", "ip", "app"))
            and success["time"] - timedelta(minutes=5)
            <= e["time"]
            < success["time"]
        ]
        if len(failures) >= 3:
            alerts.append(
                dict(
                    alert_id="rule1:" + success["id"],
                    user=success["user"],
                    ip=success["ip"],
                    application=success["app"],
                    failures=len(failures),
                    success_time=success["time"].isoformat(),
                    evidence_ids=[e["id"] for e in failures]
                    + [success["id"]],
                    disposition="Needs analyst review",
                )
            )
    return alerts


pattern = [
    event("f1", 0, "Failed"),
    event("f2", 60, "Failed"),
    event("f3", 120, "Failed"),
    event("s1", 180, "Success"),
]
tests = {
    "Failures then success": (pattern, 1),


    "One typo then success": (
        [event("a", 0, "Failed"), event("b", 60, "Success")],
        0,
    ),
    "Failures without success": (pattern[:3], 0),
    "Success before failures": (
        [event("early", -60, "Success")] + pattern[:3],
        0,
    ),
    "Failures outside five minutes": (
        pattern[:3] + [event("late", 600, "Success")],
        0,
    ),
    "Duplicates must not inflate count": (
        [pattern[0]] * 3 + [pattern[3]],
        0,
    ),
    "Exactly five-minute boundary": (
        [
            event("a", 0, "Failed"),
            event("b", 60, "Failed"),
            event("c", 120, "Failed"),
            event("d", 300, "Success"),
        ],
        1,
    ),
    "Equal timestamps not proven before": (
        [
            event("a", 0, "Failed"),
            event("b", 0, "Failed"),
            event("c", 0, "Failed"),
            event("d", 0, "Success"),
        ],
        0,
    ),
    "Other IP must not be combined": (
        pattern[:3] + [event("other", 180, "Success", ip="198.51.100.20")],
        0,
    ),
    "Legitimate repeated typos, same pattern": (pattern, 1),
}
print("Detector ready. Next cell runs its tests.")
