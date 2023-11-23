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

# Added user_type to denote admin, TA, & Student
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(50), nullable=False)

# not used as of now
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classname = db.Column(db.String(50), unique=True, nullable=False)
    ta = db.Column(db.String(50), nullable=False)

# set up to query by TA, day of the week, and each hour slot from 9am-4pm
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    TA_id = db.Column(db.Integer, nullable=False)
    day = db.Column(db.String(10), nullable=False)
    nine = db.Column(db.Boolean, nullable=False)
    ten = db.Column(db.Boolean, nullable=False)
    eleven = db.Column(db.Boolean, nullable=False)
    twelve = db.Column(db.Boolean, nullable=False)
    one = db.Column(db.Boolean, nullable=False)
    two = db.Column(db.Boolean, nullable=False)
    three = db.Column(db.Boolean, nullable=False)
    four = db.Column(db.Boolean, nullable=False)

# We may need to add a FlaskForm to collect the message data and store it from the webpage, similar to signup page/user db
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
    confirm_password = StringField('Please confirm your password:', validators=[DataRequired()])
    display_name = StringField('Please enter your first and last names:', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    user_name = StringField('Please enter your username:', validators=[DataRequired()])
    password = StringField('Please enter your password:', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Form to let student scehdule an appointment
class MakeAppt(FlaskForm):
    TA = SelectField('Please select your TA:', coerce=int, validators=[DataRequired()])
    day = SelectField('Please select the appointment day:', choices=[('Monday','Monday'),('Tuesday','Tuesday'),('Wednesday','Wednesday'),('Thursday','Thursday'),('Friday','Friday')], validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/')

def home():
        
    # checks to see if user is logged in, if not redirects to login page
    if 'user_id' not in session:
        # flash('Please log in to continue.', 'warning')
        return redirect(url_for('login'))
        
    # Only for testing currently
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
        confirm_password = form.confirm_password.data
        user_type = form.user_type.data
        display_name = form.display_name.data

        # checks if username is already taken, throws error if unavailable
        existing_user = User.query.filter_by(user_name=user_name).first()
        if existing_user:
            error = "Username already taken. Please choose a different username."
            return render_template('signup.html', form=form, error=error)
        
        # checks if passwords match and adds user to db 
        if password == confirm_password:
            user = User(user_name=user_name, password=password, user_type=user_type, display_name=display_name)
            db.session.add(user)
            db.session.commit()

            # upon creation of a new TA account, a row for each day is created in the Appointment db and all time slots are set to True
            if  user_type == 'TA':
                days = ['Monday','Tuesday','Wednesday','Thursday','Friday']
                TA_id = User.query.filter_by(user_name=user_name).first().id
                for day in days:
                    appointment = Appointment(TA_id=TA_id, day=day, nine=True, ten=True, eleven=True, twelve=True, one=True, two=True, three=True, four=True)
                    db.session.add(appointment)
                    db.session.commit()
        # throws error if password != confirm_password
        else:
            error = "Passwords do not match."
            return render_template('signup.html', form=form, error=error)
        
        return render_template('signup.html')

    return render_template('signup.html', form=form)

@app.route('/auth', methods=['GET', 'POST'])

def auth():
    # shows confirmation of new account creation
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

            if user.user_type == 'Student':
                return redirect(url_for('student'))
            
            else:
                return redirect(url_for('home'))
        else:
            # Failed login, show an error message
            # error function in signup page
            error = "Invalid credentials. Please check your username and password."
            return render_template('login.html', form=form, error=error)
    
    return render_template('login.html', form=form)

@app.route('/student', methods=['GET', 'POST'])

def student():

    TAs = User.query.filter_by(user_type='TA').all()
    TA_choices = [(ta.id, ta.display_name) for ta in TAs]

    # Form to schedule an appointment
    form = MakeAppt()
    form.TA.choices = TA_choices
    if form.validate_on_submit():
        TA = form.TA.data
        day = form.day.data
        list = []
        list.append((('9:00 a.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().nine)))
        list.append((('10:00 a.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().ten)))
        list.append((('11:00 a.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().eleven)))
        list.append((('12:00 a.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().twelve)))
        list.append((('1:00 p.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().one)))
        list.append((('2:00 p.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().two)))
        list.append((('3:00 p.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().three)))
        list.append((('4:00 p.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().four)))
        return render_template('student.html', TA=TA, day=day, list=list)

    return render_template('student.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])

def logout():

    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)