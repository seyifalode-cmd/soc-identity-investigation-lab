sessions.clear()
record("admin-revoke-sessions", "completed")
account["enabled"] = False
record("admin-disable-account", "completed")
old_access = request("/order", token=old_token)[0]
fresh_login = request("/login", {"user": "alex", "password": OLD_PASSWORD})[
    0
]
assert old_access == 401 and fresh_login == 403
print("CONTAINED: old session", old_access, "; fresh login", fresh_login)
print(
    "Verified by rejected requests, not merely by an admin success message."
)
