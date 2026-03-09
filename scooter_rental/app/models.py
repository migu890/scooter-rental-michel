from datetime import datetime
from enum import Enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager


class UserRole(str, Enum):
    PROVIDER = "provider"
    RIDER = "rider"


class ScooterStatus(str, Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)
    api_token = db.Column(db.String(64), unique=True, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    scooters = db.relationship(
        "Scooter", backref="provider", lazy=True, foreign_keys="Scooter.provider_id"
    )
    rentals = db.relationship(
        "Rental", backref="rider", lazy=True, foreign_keys="Rental.rider_id"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


class Scooter(db.Model):
    __tablename__ = "scooters"
    id = db.Column(db.Integer, primary_key=True)

    scooter_code = db.Column(db.String(64), unique=True, nullable=False)

    battery_percent = db.Column(db.Integer, nullable=False, default=100)
    latitude = db.Column(db.Float, nullable=False, default=0.0)
    longitude = db.Column(db.Float, nullable=False, default=0.0)

    status = db.Column(
        db.String(20), nullable=False, default=ScooterStatus.AVAILABLE.value
    )

    provider_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Rental(db.Model):
    __tablename__ = "rentals"
    id = db.Column(db.Integer, primary_key=True)

    scooter_id = db.Column(db.Integer, db.ForeignKey("scooters.id"), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)

    start_lat = db.Column(db.Float, nullable=False)
    start_lng = db.Column(db.Float, nullable=False)
    end_lat = db.Column(db.Float, nullable=True)
    end_lng = db.Column(db.Float, nullable=True)

    kilometers = db.Column(db.Float, nullable=False, default=0.0)

    total_price_chf = db.Column(db.Numeric(10, 2), nullable=True)

    scooter = db.relationship("Scooter", backref="rentals")
