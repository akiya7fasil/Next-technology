from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

from flask import Flask, abort, redirect, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

from db import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    init_db,
    update_user_password,
)

BASE_DIR = Path(__file__).resolve().parent
# Parent folder = project root (index.html, style.css, images/, …)
FRONTEND_ROOT = BASE_DIR.parent
DB_PATH = BASE_DIR / "data" / "app.db"

FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://127.0.0.1:5500").rstrip("/")

# Static files we allow Flask to serve (same-origin login + home after redirect)
ALLOWED_STATIC_EXT = {".html", ".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".ico", ".webp", ".map"}


def _referrer_is_live_server() -> bool:
    ref = request.referrer or ""
    return ":5500" in ref or "localhost:5500" in ref or "127.0.0.1:5500" in ref


def redirect_home():
    """After login/signup: go to real home. Live Server users → :5500; Flask-only → same host."""
    if _referrer_is_live_server():
        return redirect(f"{FRONTEND_BASE_URL}/index.html", code=303)
    return redirect("/index.html", code=303)


def redirect_login_error(msg: str):
    q = quote(msg)
    if _referrer_is_live_server():
        return redirect(f"{FRONTEND_BASE_URL}/login.html?error={q}", code=303)
    return redirect(f"/login.html?error={q}", code=303)


def redirect_signup_error(msg: str):
    q = quote(msg)
    if _referrer_is_live_server():
        return redirect(f"{FRONTEND_BASE_URL}/signup.html?error={q}", code=303)
    return redirect(f"/signup.html?error={q}", code=303)


# Demo accounts (local dev)
BUILTIN_DEMO_ACCOUNTS = (
    ("Abctech", "abctech@gmail.com"),
    ("Addistech", "addistech@gmail.com"),
    ("Addtech", "addtech@gmail.com"),
)
BUILTIN_DEMO_PASSWORD = "1234567890"


def _ensure_builtin_demo_users() -> None:
    if os.environ.get("DISABLE_BUILTIN_DEMO", "").strip() == "1":
        return
    password_hash = generate_password_hash(BUILTIN_DEMO_PASSWORD)
    for name, email in BUILTIN_DEMO_ACCOUNTS:
        user = get_user_by_email(DB_PATH, email)
        if not user:
            create_user(DB_PATH, name=name, email=email, password_hash=password_hash)
        else:
            update_user_password(DB_PATH, email, password_hash)


def _seed_demo_users() -> None:
    emails_raw = os.environ.get("SEED_EMAILS", "").strip()
    password = os.environ.get("SEED_PASSWORD", "")
    if not emails_raw or not password:
        return

    seed_name = (os.environ.get("SEED_NAME") or "User").strip() or "User"
    emails = [e.strip().lower() for e in emails_raw.split(",") if e.strip()]
    if not emails:
        return

    password_hash = generate_password_hash(password)
    for email in emails:
        if get_user_by_email(DB_PATH, email):
            continue
        name = seed_name if seed_name != "User" else email.split("@", 1)[0].replace(".", " ").title()
        create_user(DB_PATH, name=name, email=email, password_hash=password_hash)


def create_app() -> Flask:
    app = Flask(__name__)

    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    init_db(DB_PATH)
    _ensure_builtin_demo_users()
    _seed_demo_users()

    @app.get("/")
    def root():
        return redirect("/login.html", code=302)

    @app.get("/login")
    def login_alias():
        return redirect("/login.html", code=302)

    @app.get("/signup")
    def signup_alias():
        return redirect("/signup.html", code=302)

    @app.post("/signup")
    def signup():
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not name or not email or not password:
            return (
                "Missing required fields. Please go back and fill name, email, password.",
                400,
            )

        existing = get_user_by_email(DB_PATH, email)
        if existing:
            return redirect_signup_error("Email already registered. Try signing in instead.")

        password_hash = generate_password_hash(password)
        user = create_user(DB_PATH, name=name, email=email, password_hash=password_hash)
        session["user_id"] = user.id
        return redirect_home()

    @app.post("/login")
    def login():
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = get_user_by_email(DB_PATH, email)
        if not user or not check_password_hash(user.password_hash, password):
            return redirect_login_error("Invalid email or password.")

        session["user_id"] = user.id
        return redirect_home()

    @app.get("/dashboard")
    def dashboard():
        user_id = session.get("user_id")
        if not user_id:
            return redirect("/login.html", code=302)

        user = get_user_by_id(DB_PATH, int(user_id))
        if not user:
            session.clear()
            return redirect("/login.html", code=302)

        home_href = "/index.html"
        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Dashboard — NEXT</title>
    <style>
      body {{
        margin: 0;
        font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
        background: #141414;
        color: #fff;
        display: grid;
        place-items: center;
        min-height: 100vh;
      }}
      .card {{
        width: min(720px, calc(100% - 32px));
        background: #1f1f1f;
        border: 1px solid #2a2a2a;
        border-radius: 10px;
        padding: 24px;
      }}
      a {{
        color: #f77062;
        text-decoration: none;
        font-weight: 600;
      }}
      a:hover {{ text-decoration: underline; }}
      .row {{ display: flex; gap: 16px; flex-wrap: wrap; margin-top: 12px; }}
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Welcome, {user.name}!</h1>
      <p>You are logged in as <strong>{user.email}</strong>.</p>
      <div class="row">
        <a href="{home_href}">Back to website</a>
        <a href="/logout">Logout</a>
      </div>
    </div>
  </body>
</html>"""

    @app.get("/logout")
    def logout():
        session.clear()
        if _referrer_is_live_server():
            return redirect(f"{FRONTEND_BASE_URL}/login.html", code=302)
        return redirect("/login.html", code=302)

    @app.get("/images/<path:name>")
    def serve_images(name):
        if ".." in name or name.startswith(("/", "\\")):
            abort(404)
        folder = FRONTEND_ROOT / "images"
        target = (folder / name).resolve()
        if not str(target).startswith(str(folder.resolve())):
            abort(404)
        if not target.is_file():
            abort(404)
        return send_from_directory(folder, name)

    @app.get("/<path:filename>")
    def serve_frontend(filename):
        """Serve site files from project root (index.html, style.css, …)."""
        if ".." in filename or filename.startswith(("/", "\\")):
            abort(404)
        ext = Path(filename).suffix.lower()
        if ext and ext not in ALLOWED_STATIC_EXT:
            abort(404)
        path = (FRONTEND_ROOT / filename).resolve()
        if not str(path).startswith(str(FRONTEND_ROOT.resolve())):
            abort(404)
        if not path.is_file():
            abort(404)
        return send_from_directory(FRONTEND_ROOT, filename)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
