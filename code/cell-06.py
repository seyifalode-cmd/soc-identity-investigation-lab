account["password_hash"] = password_hash(NEW_PASSWORD)
account["enabled"] = True
record("admin-reset-and-enable", "completed")
assert (
    request("/login", {"user": "alex", "password": OLD_PASSWORD})[0] == 401
)
assert request("/order", token=old_token)[0] == 401
status, body = request("/login", {"user": "alex", "password": NEW_PASSWORD})
assert status == 200 and request("/order", token=body["token"])[0] == 200
print(
    "RECOVERY PASS: old password 401; old token 401; new login and order access 200."
)
Path("project1_response_audit.json").write_text(json.dumps(audit, indent=2))
server.shutdown()
server.server_close()
print("Training server stopped. No enterprise accounts were changed.")
