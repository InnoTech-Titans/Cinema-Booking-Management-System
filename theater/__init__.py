from flask import Flask,session, redirect, url_for, flash # making available the code we need to build web apps with flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import flask_login
from flask_login import LoginManager,current_user
from flask_admin import Admin, AdminIndexView, form
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, BooleanField
from flask_admin.form import Select2Widget





db = SQLAlchemy() # db object will be used to access the database when needed
bcrypt = Bcrypt()

def create_app(test_config=None):
    from .model import Movie,Screen,Projection

    app = Flask(__name__) # create an instance of the Flask class for our web app

    # set configuration variables
    app.config["SECRET_KEY"] = b"\x8c\xa5\x04\xb3\x8f\xa1<\xef\x9bY\xca/*\xff\x12\xfb"
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db' #path to database and its name
    # app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqldb://22_appweb_31:9JoOBTaL@mysql.lab.it.uc3m.es/22_appweb_31c"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #to supress warnings

    


    # register db to the current app
    db.init_app(app)

    class CustomAdminIndexView(AdminIndexView):
            @expose('/')
            def index(self):
                return self.render('admin/home.html')
            
            def is_accessible(self):
                if not current_user.is_anonymous:
                    if str(current_user.role) == "UserRole.manager":
                        return True
                    return False


            def inaccessible_callback(self, name, **kwargs):
                return redirect(url_for('auth.login'))

    my_admin = Admin(app, name='lincoln cinemas', template_mode='bootstrap3', index_view=CustomAdminIndexView())
    my_admin.add_view(ModelView(Movie, db.session))

    class ScreenAdminView(ModelView):
        column_list  = ['id','name','num_total_seats']
    my_admin.add_view(ScreenAdminView(Screen, db.session))
    class ProjectionView(BaseView):
        @expose('/')
        def index(self):
            return redirect(url_for('manager.schedule'))
        
    my_admin.add_view(ProjectionView(name="View Projections"))

    class ProjectionAddView(BaseView):
        @expose('/')
        def index(self):
            return redirect(url_for('manager.add'))
        
    my_admin.add_view(ProjectionAddView(name="Add Projection"))


    class ProjectionAdminView(ModelView):
        can_view = False
        can_edit = True
        can_delete = True
        can_create = False
    my_admin.add_view(ProjectionAdminView(Projection, db.session, name="Edit/Delete Projection"))
    

 


    class LogoutView(BaseView):
        @expose('/')
        def index(self):
            flask_login.logout_user()
            flash('You have been logged out', 'success')
            return redirect(url_for('auth.login')) 

    my_admin.add_view(LogoutView(name='Logout'))




    # User Authentication
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    # login_manager.login_message = "Login or Change role."
    login_manager.init_app(app)
    from . import model
    @login_manager.user_loader
    def load_user(user_id):
        return model.User.query.get(int(user_id))

    # register blueprints
    
    from . import main
    from . import auth
    from . import manager
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(manager.bp)

     # Create Database Models
    with app.app_context():
        db.create_all()

    return app

