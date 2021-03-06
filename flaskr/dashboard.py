from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.methods import getQuote


bp = Blueprint("dashboard", __name__)

water = 0

@bp.route("/")
def index():
    return render_template("home.html")


@bp.route("/dashboard", methods=('GET', 'POST'))
def dashboard():
    global water
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, email"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    quote = getQuote()
    if quote[1] is None:
        quote[1] = "Anonymous"
    if request.method == 'POST':
        water += int(request.form.get("extrawater"))
    return render_template("dashboard/test.html", posts=posts, water=water, quote=quote[0], author = quote[1])


@bp.route("/contact")
def contact():
    return render_template("contact.html")


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id)"
                " VALUES (?, ?, ?)",
                (title, body, g.user["id"])
            )
            db.commit()
            return redirect(url_for("dashboard.index"))

    return render_template("dashboard/create.html")


def get_post(id, check_author=True):
    post = get_db().execute(
        "SELECT p.id, title, body, created, author_id, email"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ?",
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?"
                " WHERE id = ?",
                (title, body, id)
            )
            db.commit()
            return redirect(url_for("dashboard.index"))

    return render_template("dashboard/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("dashboard.index"))

