from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.faculty_schedule import FacultySchedule
from app.models.slot_booking import SlotBooking
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut
from app.services.cache_service import FACULTY_LIST_CACHE_KEY, invalidate

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingOut])
def list_bookings(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[BookingOut]:
    bookings = (
        db.query(SlotBooking)
        .options(joinedload(SlotBooking.schedule))
        .filter(SlotBooking.student_id == current_user.id, SlotBooking.status == "booked")
        .order_by(SlotBooking.created_at.desc())
        .all()
    )
    return [BookingOut.model_validate(b) for b in bookings]


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BookingOut:
    schedule = (
        db.query(FacultySchedule)
        .filter(FacultySchedule.id == payload.faculty_schedule_id)
        .first()
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule slot not found")

    already_booked = (
        db.query(SlotBooking)
        .filter(
            SlotBooking.faculty_schedule_id == payload.faculty_schedule_id,
            SlotBooking.status == "booked",
        )
        .first()
    )
    if already_booked:
        raise HTTPException(status_code=409, detail="This slot is already booked")

    booking = SlotBooking(
        student_id=current_user.id, faculty_schedule_id=payload.faculty_schedule_id
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    # is_booked lives inside the cached faculty listing's nested schedules,
    # so a booking action invalidates it too, not just admin edits.
    invalidate(FACULTY_LIST_CACHE_KEY)
    return BookingOut.model_validate(booking)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    booking = (
        db.query(SlotBooking)
        .filter(SlotBooking.id == booking_id, SlotBooking.student_id == current_user.id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = "cancelled"
    db.commit()
    invalidate(FACULTY_LIST_CACHE_KEY)
