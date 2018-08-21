from flask import Flask, request, g, abort, jsonify
from flask.views import MethodView
from werkzeug import url_decode
from .models import Variable, VariableHistory, AccessKey
import json
import uuid


class MethodRewriteMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if "METHOD_OVERRIDE" in environ.get("QUERY_STRING", ""):
            args = url_decode(environ["QUERY_STRING"])
            method = args.get("__METHOD_OVERRIDE__")
            if method:
                method = method.encode("ascii", "replace")
                environ["REQUEST_METHOD"] = method.decode("ascii")
        return self.app(environ, start_response)


app = Flask(__name__)
app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)


@app.before_request
def parse_token():
    token = request.args.get("__TOKEN__")
    if not token:
        auth = request.headers.get("Authorization")
        if not auth:
            abort(401)

        auth_type, token = auth.split(" ", maxsplit=1)
        if auth_type != "Bearer":
            abort(401)

    try:
        g.access = AccessKey.get(key=token)
    except AccessKey.DoesNotExist:
        abort(401)


def check_permissions(path, level="read"):
    if path != g.access.path and not path.startswith(g.access.path + "/"):
        abort(401)

    if level == "write" and not g.access.is_writer:
        abort(401)

    elif level == "admin" and not g.access.is_admin:
        abort(401)

    elif level not in {"read", "write", "admin"}:
        abort(500)


class VariableView(MethodView):
    def get(self, path):
        check_permissions(path)

        children = (
            Variable.select()
            .where(Variable.path.startswith(path + "/"))
            .order_by(Variable.path)
        )

        try:
            var = Variable.get(path=path)
        except Variable.DoesNotExist:
            abort(404)

        if "full" not in request.args:
            return var.data, 200, {"Content-Type": "application/json"}

        return jsonify(
            success=True,
            error=None,
            data=dict(
                path=path,
                data=json.loads(var.data),
                children=[dict(path=c.path, data=json.loads(c.data)) for c in children],
            ),
        )

    def put(self, path):
        check_permissions(path, level="write")

        try:
            var = Variable.get(path=path)
        except Variable.DoesNotExist:
            var = Variable(path=path)

        old_data = var.data
        var.data = json.dumps(request.get_json())

        if old_data == var.data and not "force" in request.args:
            var.save()
            VariableHistory.create(path=path, data=json.dumps(request.get_json()))

        return self.get(path)


class VariableHistoryView(MethodView):
    def get(self, path):
        check_permissions(path)

        limit = int(request.args.get("limit", 10))

        entries = (
            VariableHistory.select()
            .where(VariableHistory.path == path)
            .order_by(VariableHistory.ts.desc())
            .limit(limit)
        )

        return jsonify(
            success=True,
            error=None,
            data=dict(
                path=path,
                history=[dict(ts=e.ts, data=json.loads(e.data)) for e in entries],
            ),
        )


@app.route("/key/", methods=["POST"])
def create_key():
    data = request.get_json()
    if data is None:
        abort(400)

    for field in ["access", "path"]:
        if field not in data:
            abort(400)

    if data["access"] not in {"read", "write", "admin"}:
        abort(400)

    check_permissions(data["path"])

    is_writer = data["access"] in {"write", "admin"}
    is_admin = data["access"] == "admin"

    key = str(uuid.uuid4())
    AccessKey.create(key=key, path=data["path"], is_admin=is_admin, is_writer=is_writer)

    return jsonify(success=True, error=None, data=dict(key=key))


@app.route("/key/<key>.json", methods=["DELETE"])
def delete_key(key):
    try:
        k = AccessKey.get(key=key)
    except AccessKey.DoesNotExist:
        abort(404)

    check_permissions(k.path)

    k.delete_instance()
    return jsonify(success=True, error=None)


@app.route("/var/<path:path>.txt")
def get_key_txt(path):
    check_permissions(path)
    try:
        var = Variable.get(path=path)
    except Variable.DoesNotExist:
        abort(404)

    return json.loads(var.data)


app.add_url_rule("/var/<path:path>.json", view_func=VariableView.as_view("variable"))
app.add_url_rule(
    "/var/<path:path>/history.json", view_func=VariableHistoryView.as_view("history")
)

app.debug = True
