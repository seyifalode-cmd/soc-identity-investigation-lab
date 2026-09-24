incoming = queue.Queue()
emitted, seen, history = [], set(), []


def alert_worker():
    while True:
        item = incoming.get()
        try:
            if item is None:
                return
            history.append(item)
            for alert in detect(history):
                if alert["alert_id"] not in seen:
                    seen.add(alert["alert_id"])
                    emitted.append(alert)
                    print(
                        "AUTOMATIC ALERT:",
                        alert["user"],
                        "-",
                        alert["failures"],
                        "failures before success",
                    )
        finally:
            incoming.task_done()


worker = threading.Thread(target=alert_worker, daemon=True)
worker.start()
for row in pattern + [pattern[-1]]:
    incoming.put(row)
    time.sleep(0.15)
incoming.put(None)
worker.join(timeout=5)
assert not worker.is_alive(), "Worker did not stop"
assert len(emitted) == 1
Path("project1_alerts.jsonl").write_text(
    "\n".join(json.dumps(a) for a in emitted) + "\n"
)
print("PASS: one alert, repeated delivery suppressed, worker stopped.")
print(json.dumps(emitted[0], indent=2))
