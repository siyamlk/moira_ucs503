from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_current_admin_user
from app.database.connection import get_db
from app.models.faculty_schedule import FacultySchedule
from app.models.slot_booking import SlotBooking
from app.models.user import User
from app.schemas.admin import AdminBookingOut
from app.schemas.faculty import ScheduleOut
from app.services.audit_service import record_audit
from app.services.cache_service import FACULTY_LIST_CACHE_KEY, invalidate

router = APIRouter(prefix="/api/admin/bookings", tags=["admin-bookings"])


def _to_out(booking: SlotBooking) -> AdminBookingOut:
    return AdminBookingOut(
        id=booking.id,
        student_id=booking.student_id,
        student_name=booking.student.full_name,
        student_email=booking.student.email,
        faculty_id=booking.schedule.faculty_id,
        faculty_name=booking.schedule.faculty.name,
        schedule=ScheduleOut.model_validate(booking.schedule),
        status=booking.status,
        created_at=booking.created_at,
    )


@router.get("", response_model=list[AdminBookingOut])
def list_bookings(
    faculty_id: int | None = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> list[AdminBookingOut]:
    query = db.query(SlotBooking).options(
        joinedload(SlotBooking.student),
        joinedload(SlotBooking.schedule).joinedload(FacultySchedule.faculty),
    )
    if faculty_id is not None:
        query = query.join(
            FacultySchedule, SlotBooking.faculty_schedule_id == FacultySchedule.id
        ).filter(FacultySchedule.faculty_id == faculty_id)
    bookings = query.order_by(SlotBooking.created_at.desc()).all()
    return [_to_out(b) for b in bookings]


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    """Lets an admin force-cancel any student's booking — e.g. a professor
    cancelling their office hours. Distinct from DELETE /api/bookings/{id},
    which only lets a student cancel their own."""
    booking = db.query(SlotBooking).filter(SlotBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = "cancelled"
    record_audit(
        db, current_user.id, "delete", "slot_booking", booking.id, {"student_id": booking.student_id}
    )
    db.commit()
    invalidate(FACULTY_LIST_CACHE_KEY)
