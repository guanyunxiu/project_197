from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.db.models import F
from datetime import timedelta
from .models import BorrowRecord, Reservation, Book, FineRecord
from django.conf import settings


def check_overdue_books():
    now = timezone.now()
    overdue_records = BorrowRecord.objects.filter(
        status__in=['borrowed'],
        due_date__lt=now
    )
    for record in overdue_records:
        record.status = 'overdue'
        fine_per_day = float(getattr(settings, 'LIBRARY_CONFIG', {}).get('FINE_PER_DAY', 0.5))
        days_overdue = (now - record.due_date).days
        record.fine_amount = days_overdue * fine_per_day
        record.save()


def update_reservation_status():
    now = timezone.now()
    expired_reservations = Reservation.objects.filter(
        status__in=['pending', 'available'],
        expire_date__lt=now
    )
    for reservation in expired_reservations:
        reservation.status = 'expired'
        reservation.save()
        book = reservation.book
        book.reservation_count = F('reservation_count') - 1
        book.save()
        book.refresh_from_db()
        book.update_status()

    pending_reservations = Reservation.objects.filter(
        status='pending'
    ).order_by('book_id', 'queue_position')

    current_book_id = None
    current_queue = 1
    for reservation in pending_reservations:
        if reservation.book_id != current_book_id:
            current_book_id = reservation.book_id
            current_queue = 1

        book = reservation.book
        if book.available_quantity > 0 and current_queue == 1:
            reservation.status = 'available'
            reservation.available_notify_date = now
            expire_days = int(getattr(settings, 'LIBRARY_CONFIG', {}).get('RESERVATION_EXPIRE_DAYS', 3))
            reservation.expire_date = now + timedelta(days=expire_days)
            reservation.save()

        reservation.queue_position = current_queue
        reservation.save()
        current_queue += 1


def update_book_status():
    books = Book.objects.all()
    for book in books:
        book.update_status()


def auto_generate_fines():
    now = timezone.now()
    fine_per_day = float(getattr(settings, 'LIBRARY_CONFIG', {}).get('FINE_PER_DAY', 0.5))

    overdue_records = BorrowRecord.objects.filter(
        status='overdue',
        fine_paid=False
    )

    for record in overdue_records:
        days_overdue = (now - record.due_date).days
        new_fine = days_overdue * fine_per_day
        if new_fine > record.fine_amount:
            record.fine_amount = new_fine
            record.save()

            existing_fine = FineRecord.objects.filter(
                borrow_record=record,
                status='unpaid'
            ).first()

            if existing_fine:
                existing_fine.amount = new_fine
                existing_fine.days_overdue = days_overdue
                existing_fine.save()
            else:
                FineRecord.objects.create(
                    reader=record.reader,
                    borrow_record=record,
                    book=record.book,
                    fine_type='overdue',
                    amount=new_fine,
                    days_overdue=days_overdue,
                    status='unpaid'
                )


def start_scheduler():
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)

    scheduler.add_job(check_overdue_books, 'interval', minutes=60, id='check_overdue_books')
    scheduler.add_job(update_reservation_status, 'interval', minutes=30, id='update_reservation_status')
    scheduler.add_job(auto_generate_fines, 'interval', minutes=120, id='auto_generate_fines')
    scheduler.add_job(update_book_status, 'interval', minutes=180, id='update_book_status')

    scheduler.start()
    return scheduler
