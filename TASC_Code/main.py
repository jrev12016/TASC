from flask import Flask, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SubmitField, IntegerField, BooleanField, SelectField
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired

app = Flask (__name__)

app.config['SECRET_KEY'] = 'oursecretkey'
# setups the database called TASC
# new folder 'instance' will be created in root directory of app file

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TASC.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

""" Added user_type to denote admin, TA, & Student """
class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(50), nullable=False)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classname = db.Column(db.String(50), unique=True, nullable=False)
    ta = db.Column(db.String(50), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    available = db.Column(db.Boolean, nullable=False)
    filled = db.Column(db.Boolean, nullable=False)
    ta = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.Float, nullable=False)

""" We may need to add a FlaskForm to collect the message data and store it from the webpage, similar to signup page/user db """
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.Float, nullable=False)

class SignupForm(FlaskForm):
    user_type = SelectField('Please select user type:', choices=[('Admin', 'Admin'), ('TA', 'TA'), ('Student', 'Student')], validators=[DataRequired()])
    user_name = StringField('Please enter your username:', validators=[DataRequired()])
    password = StringField('Please enter your password:', validators=[DataRequired()])
    display_name = StringField('Please enter your first and last names:', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    user_name = StringField('Please enter your username:', validators=[DataRequired()])
    password = StringField('Please enter your password:', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')

def home():

        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        
        user_id = User.query.get(session['user_id']).id
        user_name = User.query.get(session['user_id']).user_name
        user_type = User.query.get(session['user_id']).user_type
        display_name = User.query.get(session['user_id']).display_name
        
        return render_template('home.html', user_id=user_id, user_name=user_name, user_type=user_type, display_name=display_name)

@app.route('/signup', methods=['GET','POST'])

def signup():

    form = SignupForm()
    if form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data
        user_type = form.user_type.data
        display_name = form.display_name.data

        existing_user = User.query.filter_by(user_name=user_name).first()
        if existing_user:
            error = "Username already taken. Please choose a different username."
            return render_template('signup.html', form=form, error=error)
        
        user = User(user_name=user_name, password=password, user_type=user_type, display_name=display_name)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('auth'))

    return render_template('signup.html', form=form)

@app.route('/auth', methods=['GET', 'POST'])

def auth():

    return render_template('auth.html')

@app.route ('/login', methods=['GET', 'POST'])

def login():

    form = LoginForm()  
    if form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data
        
        user = User.query.filter_by(user_name=user_name).first()        

        # check for correct user_name and password
        if user and password == user.password:
            session['user_id'] = user.id
            session['user_name'] = user_name.capitalize()
            session['user_type'] = user.user_type
            session['display_name'] = user.display_name
            return redirect(url_for('home'))
        else:
            # Failed login, show an error message
            # error function in signup page
            error = "Invalid credentials. Please check your username and password."
            return render_template('login.html', form=form, error=error)
    
    return render_template('login.html', form=form)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)