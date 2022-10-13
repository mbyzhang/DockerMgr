from flask import Flask, request, redirect, url_for, render_template, flash
from flask_bootstrap import Bootstrap5
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
import docker
import docker.errors
from config import *
from constants import *
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY

bootstrap = Bootstrap5(app)
auth = HTTPBasicAuth()

docker_cli = docker.from_env()


@auth.verify_password
def verify_password(username, password):
    if username == AUTH_USERNAME and check_password_hash(AUTH_PASSWORD, password):
        return username


@app.route("/")
def handle_home():
    return redirect(url_for("handle_container_list"))


@app.route("/containers", methods=["GET"])
@auth.login_required
def handle_container_list():
    containers = docker_cli.containers.list(
        all=True, filters={"ancestor": DOCKER_IMAGE})
    return render_template("containers.html", containers=containers)


@app.route("/containers/<container_id>/logs", methods=["GET"])
@auth.login_required
def handle_container_logs(container_id):
    container = docker_cli.containers.get(container_id)
    logs = container.logs(tail=1000)
    return render_template("container_logs.html", container=container, logs=logs.decode("utf-8", "ignore"))


@app.route("/containers", methods=["POST"])
@auth.login_required
def handle_container_action():
    action = request.form.get("action", ACTION_CREATE)
    container_id = request.form.get("id")

    try:
        if action == ACTION_CREATE:
            name = request.form.get("name") or None
            docker_cli.containers.run(
                DOCKER_IMAGE,
                detach=True,
                name=name,
                **DOCKER_RUN_KWARGS,
            )
        elif action == ACTION_REMOVE:
            docker_cli.containers.get(container_id).remove()
        elif action == ACTION_STOP:
            docker_cli.containers.get(container_id).stop()
        elif action == ACTION_START:
            docker_cli.containers.get(container_id).start()
        else:
            raise BadRequest("Invalid action")
    except docker.errors.DockerException as e:
        flash(f"{e.__class__.__name__}: {e}", "error")

    containers = docker_cli.containers.list(
        all=True,
        filters={"ancestor": DOCKER_IMAGE}
    )

    return render_template(
        "containers.html",
        containers=containers,
    )
