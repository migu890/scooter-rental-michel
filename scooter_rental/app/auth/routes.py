import secrets
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.extensions import db
from app.models import User
from .forms import RegisterForm, LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        if existing:
            flash("Benutzername oder E-Mail existiert bereits.", "danger")
            return render_template("auth_register.html", form=form)

        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip(),
            role=form.role.data,
        )
        user.set_password(form.password.data)

        # Token für API-Auth ohne Browser (Anforderung)
        user.api_token = secrets.token_hex(32)

        db.session.add(user)
        db.session.commit()

        flash("Registrierung erfolgreich. Bitte einloggen.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth_register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        ident = form.username.data.strip()
        user = User.query.filter(
            (User.username == ident) | (User.email == ident)
        ).first()

        if not user or not user.verify_password(form.password.data):
            flash("Login fehlgeschlagen.", "danger")
            return render_template("auth_login.html", form=form)

        login_user(user)

        # Rollenbasiertes Redirect (damit Rider nicht auf Provider-Seite landen)
        if user.role == "provider":
            return redirect(url_for("web.scooters"))
        return redirect(url_for("web.dashboard"))

    return render_template("auth_login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Ausgeloggt.", "info")
    return redirect(url_for("auth.login"))
