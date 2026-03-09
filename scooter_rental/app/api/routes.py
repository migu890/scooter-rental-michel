from flask import Blueprint, request, jsonify
from app.models import User, Scooter, Rental

api_bp = Blueprint("api", __name__)


def token_user():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header.removeprefix("Bearer ").strip()
    if not token:
        return None
    return User.query.filter_by(api_token=token).first()


@api_bp.route("/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    ident = (data.get("username") or "").strip()
    pwd = data.get("password") or ""

    user = User.query.filter((User.username == ident) | (User.email == ident)).first()
    if not user or not user.verify_password(pwd):
        return jsonify({"error": "invalid credentials"}), 401

    if not user.api_token:
        import secrets

        user.api_token = secrets.token_hex(32)
        from app.extensions import db

        db.session.commit()

    return jsonify({"token": user.api_token})


@api_bp.route("/scooters", methods=["GET"])
def api_scooters():
    scooters = Scooter.query.all()
    return jsonify(
        [
            {
                "code": s.scooter_code,
                "battery_percent": s.battery_percent,
                "status": s.status,
                "lat": s.latitude,
                "lng": s.longitude,
            }
            for s in scooters
        ]
    )


@api_bp.route("/rentals/me", methods=["GET"])
def api_rentals_me():
    user = token_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    rentals = (
        Rental.query.filter_by(rider_id=user.id)
        .order_by(Rental.id.desc())
        .limit(50)
        .all()
    )
    return jsonify(
        [
            {
                "id": r.id,
                "scooter": r.scooter.scooter_code,
                "start_time": r.start_time.isoformat(),
                "end_time": r.end_time.isoformat() if r.end_time else None,
                "kilometers": float(r.kilometers),
                "price_chf": (
                    str(r.total_price_chf) if r.total_price_chf is not None else None
                ),
            }
            for r in rentals
        ]
    )
