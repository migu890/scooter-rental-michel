from datetime import datetime
from ..extensions import db
from ..models import Scooter, Rental, ScooterStatus, UserRole
from .pricing import calculate_price_minutes


class RentalError(Exception):
    pass


def start_rental(*, rider, scooter_code: str, lat: float, lng: float) -> Rental:
    if rider.role != "rider":
        raise RentalError("Only riders can start rentals.")

    scooter = Scooter.query.filter_by(
        scooter_code=scooter_code.strip(), status="available"
    ).first()

    if not scooter:
        raise RentalError("Scooter not found or not available.")

    scooter.status = "rented"

    rental = Rental(
        scooter_id=scooter.id,
        rider_id=rider.id,
        start_time=datetime.utcnow(),
        start_lat=lat,
        start_lng=lng,
    )

    db.session.add(rental)
    db.session.commit()
    return rental


def end_rental(
    *, rider, rental_id: int, kilometers: float, lat: float, lng: float
) -> Rental:
    rental = Rental.query.get(rental_id)
    if not rental:
        raise RentalError("Rental not found.")
    if rental.rider_id != rider.id:
        raise RentalError("Not your rental.")
    if rental.end_time is not None:
        raise RentalError("Rental already ended.")

    rental.end_time = datetime.utcnow()
    rental.kilometers = max(0.0, float(kilometers))
    rental.end_lat = lat
    rental.end_lng = lng

    duration_seconds = (rental.end_time - rental.start_time).total_seconds()
    minutes = int(duration_seconds // 60)
    rental.total_price_chf = calculate_price_minutes(minutes)

    scooter = rental.scooter
    scooter.status = ScooterStatus.AVAILABLE.value
    scooter.latitude = lat
    scooter.longitude = lng

    db.session.commit()
    return rental
