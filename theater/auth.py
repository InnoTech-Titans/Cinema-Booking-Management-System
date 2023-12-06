# from flask import Blueprint, render_template, request, redirect, url_for, flash
# import flask_login

# from . import db, bcrypt

# from . import model

# from enum import Enum

# bp = Blueprint("auth", __name__)

# class UserRole(Enum):
#     customer = 1
#     manager = 2
#     frontdesk = 3




# @bp.route("/signup", methods=["POST"])
# def signup_post():
#     email = request.form.get("email")
#     username = request.form.get("username")
#     password = request.form.get("password")
#     role = request.form.get("role")
#     # Check that passwords are equal
#     if password != request.form.get("password_repeat"):
#         flash("Passwords are different. Try again.", 'error')
#         return redirect(url_for("auth.signup"))

#     # Only specific company email can Sign Up as a manager. Change email to employees email (MANAGER)
#     if role == 'manager' and (email != "test@test.com" and email != "manager@manager.com"): 
#         flash("You cannot Sign Up as a manager", 'error')
#         return redirect(url_for("auth.signup"))
    
#     # Check if the email is already at the database
#     user = model.User.query.filter_by(email=email).first()
#     if user:
#         flash("Email you provided is already registered.", 'error')
#         return redirect(url_for("auth.signup"))
 
#     if role == 'manager':
#         role = model.UserRole.manager
#     else:
#         role = model.UserRole.customer
    
#     # Only specific company email can Sign Up as a admin. Change email to employees email (ADMIN)
#     if role == 'admin' and (email != "test@admin.com" and email != "admin@admin.com"): 
#         flash("You cannot Sign Up as a admin", 'error')
#         return redirect(url_for("auth.signup"))
    
#     # Check if the email is already at the database
#     user = model.User.query.filter_by(email=email).first()
#     if user:
#         flash("Email you provided is already registered.", 'error')
#         return redirect(url_for("auth.signup"))
 
#     if role == 'admin':
#         role = model.UserRole.admin
#     else:
#         role = model.UserRole.manager
    
#     if role == 'frontdesk' and (email != "test@frontdesk.com" and email != "frontdesk@frontdesk.com"): 

#         flash("You cannot Sign Up as a frontdesk", 'error')
#         return redirect(url_for("auth.signup"))
    
#     # Check if the email is already at the database
#     user = model.User.query.filter_by(email=email).first()
#     if user:
#         flash("Email you provided is already registered.", 'error')
#         return redirect(url_for("auth.signup"))
    

#     if UserRole(request.form['role']) == 'frontdesk':
#         print(type(role))
        
#         role = model.UserRole.frontdesk
#     else:
#         role = model.UserRole.manager

#     password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
#     new_user = model.User(email=email, name=username, password=password_hash, role=role)
#     db.session.add(new_user)
#     db.session.commit()
#     flash("You have successfully signed up!", 'success')
#     return redirect(url_for("auth.login"))


# @bp.route("/login")
# def login():
#     return render_template("auth/login.html")


# @bp.route("/login", methods=["POST"])
# def login_post():
#     email = request.form.get("email")
#     password = request.form.get("password")
#     # Check that passwords are equal
#     if password != request.form.get("password_repeat"):
#         flash("Passwords are different. Try again.", 'error')
#         return redirect(url_for("auth.login"))
#     # Get the user with that email from the database:
#     user = model.User.query.filter_by(email=email).first()
#     if user and bcrypt.check_password_hash(user.password, password):
#         # The user exists and the password is correct
#         flask_login.login_user(user)
#         flash("You have successfully logged!", 'success')
#         return redirect(url_for("main.index"))
#     else:
#         # Wrong email and/or password
#         if user == None:
#             flash("User not registered. Go to Sign Up.", 'error')
#             return redirect(url_for("auth.login"))
#         if user.email == email and bcrypt.check_password_hash(user.password, password) == 0:
#             flash("Wrong password", 'error')
#         return redirect(url_for("auth.login"))

# @bp.route("/logout")
# @flask_login.login_required
# def logout():
#     flask_login.logout_user()
#     flash ('You have been logged out', 'success')
#     return redirect(url_for("auth.login"))

from flask import Blueprint, render_template, request, redirect, url_for, flash
import flask_login

from . import db, bcrypt

from . import model

from enum import Enum

bp = Blueprint("auth", __name__)

class UserRole(Enum):
    customer = 1
    manager = 2
    frontdesk = 3
    

@bp.route("/signup")
def signup():
    return render_template("auth/signup.html")

@bp.route('/signup', methods=['POST'])
def signup_post():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        role_str = request.form.get("role")
        password_repeat = request.form.get("password_repeat")

        if password != password_repeat:
            flash("Passwords do not match. Please try again.", 'error')
        else:
            role_mapping = {
                'customer': model.UserRole.customer,
                'manager': model.UserRole.manager,
                'frontdesk': model.UserRole.frontdesk,
            }
            
            if role_str in role_mapping:
                role = role_mapping[role_str]
            else:
                flash("Invalid role selected.", 'error')
                return redirect(url_for('auth.signup'))

            existing_user = model.User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already registered. Please log in.", 'error')
                return redirect(url_for('auth.login'))
            
            password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
            new_user = model.User(email=email, name=username, password=password_hash, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash("You have successfully signed up!", 'success')
            return redirect(url_for('auth.login'))

    return render_template('signup.html')

@bp.route("/login")
def login():
    return render_template("auth/login.html")


@bp.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    # Check that passwords are equal
    if password != request.form.get("password_repeat"):
        flash("Passwords are different. Try again.", 'error')
        return redirect(url_for("auth.login"))
    # Get the user with that email from the database:
    user = model.User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        # The user exists and the password is correct
        flask_login.login_user(user)
        flash("You have successfully logged!", 'success')
        return redirect(url_for("main.index"))
    else:
        # Wrong email and/or password
        if user == None:
            flash("User not registered. Go to Sign Up.", 'error')
            return redirect(url_for("auth.login"))
        if user.email == email and bcrypt.check_password_hash(user.password, password) == 0:
            flash("Wrong password", 'error')
        return redirect(url_for("auth.login"))

@bp.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    flash ('You have been logged out', 'success')
    return redirect(url_for("auth.login"))
