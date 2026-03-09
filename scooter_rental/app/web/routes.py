from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Scooter, Rental
from app.services.rental_service import start_rental, end_rental, RentalError

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("web.dashboard"))
    return redirect(url_for("auth.login"))


@web_bp.route("/dashboard")
@login_required
def dashboard():
    active_rental = None
    available_scooters = []

    if current_user.role == "rider":
        active_rental = Rental.query.filter_by(
            rider_id=current_user.id, end_time=None
        ).first()

        available_scooters = Scooter.query.filter_by(status="available").all()

    return render_template(
        "dashboard.html",
        active_rental=active_rental,
        available_scooters=available_scooters,
    )


@web_bp.route("/scooters", methods=["GET", "POST"])
@login_required
def scooters():
    if current_user.role != "provider":
        abort(403)

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        battery = int(request.form.get("battery", "100"))
        lat = float(request.form.get("lat", "0"))
        lng = float(request.form.get("lng", "0"))

        if not code:
            flash("Scooter-Code ist erforderlich.", "danger")
            return redirect(url_for("web.scooters"))

        if Scooter.query.filter_by(scooter_code=code).first():
            flash("Scooter-Code existiert bereits.", "danger")
            return redirect(url_for("web.scooters"))

        s = Scooter(
            scooter_code=code,
            battery_percent=max(0, min(100, battery)),
            latitude=lat,
            longitude=lng,
            status="available",
            provider_id=current_user.id,
        )
        db.session.add(s)
        db.session.commit()
        flash("Scooter hinzugefügt.", "success")
        return redirect(url_for("web.scooters"))

    my_scooters = Scooter.query.filter_by(provider_id=current_user.id).all()
    return render_template("scooters.html", scooters=my_scooters)


@web_bp.route("/scooter/<int:scooter_id>/edit", methods=["POST"])
@login_required
def scooter_edit(scooter_id):
    if current_user.role != "provider":
        abort(403)

    s = Scooter.query.get_or_404(scooter_id)
    if s.provider_id != current_user.id:
        abort(403)

    s.status = request.form.get("status", s.status)
    s.battery_percent = int(request.form.get("battery", s.battery_percent))
    s.latitude = float(request.form.get("lat", s.latitude))
    s.longitude = float(request.form.get("lng", s.longitude))

    db.session.commit()
    flash("Scooter aktualisiert.", "success")
    return redirect(url_for("web.scooters"))


@web_bp.route("/scooter/<int:scooter_id>/delete", methods=["POST"])
@login_required
def scooter_delete(scooter_id):
    if current_user.role != "provider":
        abort(403)

    s = Scooter.query.get_or_404(scooter_id)
    if s.provider_id != current_user.id:
        abort(403)

    db.session.delete(s)
    db.session.commit()
    flash("Scooter gelöscht.", "success")
    return redirect(url_for("web.scooters"))


@web_bp.route("/rent/start", methods=["POST"])
@login_required
def rent_start():
    if current_user.role != "rider":
        abort(403)

    code = request.form.get("code", "").strip()
    lat = float(request.form.get("lat", "0"))
    lng = float(request.form.get("lng", "0"))

    if not code:
        flash("Bitte einen Scooter auswählen.", "danger")
        return redirect(url_for("web.dashboard"))

    try:
        r = start_rental(rider=current_user, scooter_code=code, lat=lat, lng=lng)
        flash(f"Miete gestartet (id={r.id}).", "success")
    except RentalError as e:
        flash(str(e), "danger")

    return redirect(url_for("web.dashboard"))


@web_bp.route("/rent/end", methods=["POST"])
@login_required
def rent_end():
    if current_user.role != "rider":
        abort(403)

    rental_id = int(request.form.get("rental_id"))
    km = float(request.form.get("km", "0"))
    lat = float(request.form.get("lat", "0"))
    lng = float(request.form.get("lng", "0"))

    try:
        r = end_rental(
            rider=current_user, rental_id=rental_id, kilometers=km, lat=lat, lng=lng
        )
        flash(f"Miete beendet. Preis CHF {r.total_price_chf}", "success")
    except RentalError as e:
        flash(str(e), "danger")

    return redirect(url_for("web.dashboard"))
