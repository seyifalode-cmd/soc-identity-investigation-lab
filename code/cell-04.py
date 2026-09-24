from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError

if "server" in globals():
    server.shutdown()
    server.server_close()
OLD_PASSWORD = "Lab-only-before-482!"
NEW_PASSWORD = "Lab-only-after-729!"
salt = secrets.token_bytes(16)


def password_hash(value):
    return hashlib.pbkdf2_hmac("sha256", value.encode(), salt, 100000)


account = {
    "user": "alex",
    "enabled": True,
    "password_hash": password_hash(OLD_PASSWORD),
}
sessions, audit = {}, []


def record(action, result):
    audit.append(
        {
            "time": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "result": result,
        }
    )


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_POST(self):
        if self.path != "/login":
            return self.reply(404, {"error": "unknown route"})
        data = json.loads(
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
        )
        if not account["enabled"]:
            record("login", "blocked-disabled")
            return self.reply(403, {"error": "account disabled"})
        if data.get("user") != "alex" or not hmac.compare_digest(
            password_hash(data.get("password", "")),
            account["password_hash"],
        ):
            record("login", "bad-credentials")
            return self.reply(401, {"error": "bad credentials"})


        token = secrets.token_urlsafe(24)
        sessions[token] = "alex"
        record("login", "success")
        self.reply(200, {"token": token})

    def do_GET(self):
        if self.path != "/order":
            return self.reply(404, {"error": "unknown route"})
        token = self.headers.get("Authorization", "").removeprefix(
            "Bearer "
        )
        if token not in sessions:
            record("view-order", "rejected-session")
            return self.reply(401, {"error": "invalid session"})
        if not account["enabled"]:
            record("view-order", "blocked-disabled")
            return self.reply(403, {"error": "account disabled"})
        record("view-order", "success")
        self.reply(
            200,
            {"order": "TRAINING-1042", "contents": "fictional test order"},
        )


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
base_url = "http://127.0.0.1:" + str(server.server_port)


def request(path, payload=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = Request(
        base_url + path,
        data=json.dumps(payload).encode() if payload else None,
        headers=headers,
    )
    try:
        with urlopen(req, timeout=3) as response:
            return response.status, json.loads(response.read())
    except HTTPError as err:
        return err.code, json.loads(err.read())


status, body = request("/login", {"user": "alex", "password": OLD_PASSWORD})
assert status == 200
old_token = body["token"]
assert request("/order", token=old_token)[0] == 200
print("BEFORE containment: login 200; protected order access 200.")
