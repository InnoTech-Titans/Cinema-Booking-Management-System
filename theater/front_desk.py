from flask import Blueprint, render_template, request, flash, url_for, redirect
import flask_login
from flask_login import current_user
from . import model
from . import db

bp = Blueprint("main", __name__)

@bp.route("/reservation/", defaults={'id': None})
@bp.route("/reservation/<int:id>")
@flask_login.login_required
def reservation(id):
    current_day = date.today()
    current_time = datetime.now()
    all_projections = model.Projection.query.filter(model.Projection.day >= current_day).order_by(model.Projection.day.asc(), model.Projection.time.asc()).all()
    
    if id is None:
        return render_template("reservation.html", projection=None, projections=all_projections)
    else:
        projection = model.Projection.query.get(id)
        projections = model.Projection.query.filter(model.Projection.movie_id == projection.movie_id, model.Projection.day >= current_day).order_by(model.Projection.day.asc(), model.Projection.time.asc()).all()
        return render_template("reservation.html", projection=projection, projections=projections)

@bp.route("/reservation/", methods=["POST"])
@flask_login.login_required
def reservation_post():
    payment_method = request.form.get("payment_method")

    if payment_method == "cash":
        chosen_projection = request.form.get("projection")
        chosen_num_seats = request.form.get("seats")
        projection = model.Projection.query.get(chosen_projection)
        new_reservation = model.Reservation(user_id=current_user.id, projection_id=projection.id, num_seats=int(chosen_num_seats), date_time=datetime.now())
        db.session.add(new_reservation)
        db.session.commit()
        flash(f"You have bought {chosen_num_seats} tickets for {projection.movie.title}", 'success')
    elif payment_method in ("credit_card", "debit_card"):
        chosen_projection = request.form.get("projection")
        chosen_num_seats = request.form.get("seats")
        price = request.form.get('price_main')
        # Handle payment processing here
        return render_template("payments.html", proj=chosen_projection, seats=chosen_num_seats, mode=payment_method, price=price)

    return redirect(url_for("main.index"))

@bp.route("/cancel_ticket/<int:id>", methods=["POST"])
@flask_login.login_required
def cancel_ticket(id):
    # Check if the user has the permission to cancel this ticket
    reservation = model.Reservation.query.get(id)

    if reservation is not None and reservation.user_id == current_user.id:
        db.session.delete(reservation)
        db.session.commit()
        flash("Ticket has been canceled.", "success")
    else:
        flash("Ticket cancellation failed. You do not have permission to cancel this ticket.", "error")

    return redirect(url_for("main.user"))
