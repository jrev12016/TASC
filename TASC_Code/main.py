from flask import Flask, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SubmitField, IntegerField, BooleanField, SelectField
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired
from flask_login import current_user # currently not being used
from flask import request
from wtforms import StringField, SubmitField, validators

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

    # added relationship for TA
    #classes = db.relationship('Class', secondary='ta_class_association', backref=db.backref('tas', lazy='dynamic'))

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classname = db.Column(db.String(50), nullable=False) #took out unique = true
    ta_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # changed to integer from String of length 50 #also added db.ForeignKey

# set up to query by TA, day of the week, and each hour slot from 9am-4pm
# created another table below to allow for this^
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

class TAAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ta_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    monday_start = db.Column(db.Time)
    monday_end = db.Column(db.Time)
    tuesday_start = db.Column(db.Time)
    tuesday_end = db.Column(db.Time)
    wednesday_start = db.Column(db.Time)
    wednesday_end = db.Column(db.Time)
    thursday_start = db.Column(db.Time)
    thursday_end = db.Column(db.Time)
    friday_start = db.Column(db.Time)
    friday_end = db.Column(db.Time)

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

# Form to let TAs submit/create a class
class AddClassForm(FlaskForm):
    classname = StringField('Class Name', validators=[DataRequired()])
    submit = SubmitField('Add Class')

# Form to let TAs submit their availability
class UpdateAvailabilityForm(FlaskForm):
    monday_start = StringField('Monday Start Time', validators=[validators.Regexp(r'^\d{2}:\d{2}$', message='Invalid time format (HH:MM)')])
    monday_end = StringField('Monday End Time', validators=[validators.Regexp(r'^\d{2}:\d{2}$', message='Invalid time format (HH:MM)')])

    tuesday_start = StringField('Tuesday Start Time', validators=[validators.Regexp(r'^\d{2}:\d{2}$', message='Invalid time format (HH:MM)')])
    tuesday_end = StringField('Tuesday End Time', validators=[validators.Regexp(r'^\d{2}:\d{2}$', message='Invalid time format (HH:MM)')])

    wednesday_start = StringField('Wednesday Start Time', validators=[validators.Regexp(r'^\d{2}:\d{2}$', message='Invalid time format (HH:MM)')])
    wednesday_end = StringField('Wednesday End Time', validators=[validators.Regexp(r'^\d{2}:\d{2}$', message='Invalid time format (HH:MM)')])

    thursday_start = StringField('Thursday Start Time', validators=[validators.Regexp(r'^\d{2}:\d{2}$', message='Invalid time format (HH:MM)')])
    thursday_end = StringField('Thursday End Time', validators=[validators.Regexp(r'^\d{2}:\d{2}$', message='Invalid time format (HH:MM)')])

    friday_start = StringField('Friday Start Time', validators=[validators.Regexp(r'^\d{2}:\d{2}$', message='Invalid time format (HH:MM)')])
    friday_end = StringField('Friday End Time', validators=[validators.Regexp(r'^\d{2}:\d{2}$', message='Invalid time format (HH:MM)')])

    submit = SubmitField('Update Availability')

# Default page changed from home to signup
@app.route('/', methods=['GET','POST'])

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

@app.route('/home', methods=['GET','POST'])
    
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
            elif user.user_type == 'TA':
                return redirect(url_for('ta'))
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
        
        # Only display available times
        list_available = []
        for times in list:
            time, conditional = times
            if conditional:
                list_available.append(time)
            
        return render_template('student.html', TA=TA, day=day, list_available=list_available)

    return render_template('student.html', form=form)

@app.route('/ta', methods=['GET', 'POST'])
def ta():
    add_class_form = AddClassForm()
    update_availability_form = UpdateAvailabilityForm()

    ta_id = session['user_id']
    
    # Retrieve TA availability outside the form validation block
    ta_availability = TAAvailability.query.filter_by(ta_id=ta_id).first()

    if request.method == 'POST':
        # handles adding a class
        if add_class_form.validate_on_submit():
            classname = add_class_form.classname.data

            # Create a new class entry
            new_class = Class(classname=classname, ta_id=ta_id)
    
            try:
                db.session.add(new_class)
                db.session.commit()
                flash('Class added successfully!', 'success') 
            except Exception as e:
                print(f"Error committing ta changes: {e}")
                db.session.rollback()

        # handles changing availability
        elif update_availability_form.validate_on_submit():
            print("Form is valid. Processing availability update.")
            # Update availability for the new class
            if ta_availability is None:
                ta_availability = TAAvailability(ta_id=ta_id)

            ta_availability.monday_start = update_availability_form.monday_start.data
            ta_availability.monday_end = update_availability_form.monday_end.data

            ta_availability.tuesday_start = update_availability_form.tuesday_start.data
            ta_availability.tuesday_end = update_availability_form.tuesday_end.data

            ta_availability.wednesday_start = update_availability_form.wednesday_start.data
            ta_availability.wednesday_end = update_availability_form.wednesday_end.data

            ta_availability.thursday_start = update_availability_form.thursday_start.data
            ta_availability.thursday_end = update_availability_form.thursday_end.data

            ta_availability.friday_start = update_availability_form.friday_start.data
            ta_availability.friday_end = update_availability_form.friday_end.data

            print("debug point 1")
            print(ta_availability)

            try:
                db.session.add(ta_availability)
                db.session.commit()
                print("debug point 2")
                flash('Availability updated successfully!', 'success')
            except Exception as e:
                print(f"Error committing availability changes: {e}")
                db.session.rollback()
        else:
            print("form validation failed")
            print(update_availability_form.errors)

        return redirect(url_for('ta'))
   
    ta_username = session.get('user_name')
    enrolled_classes = Class.query.filter_by(ta_id=ta_id).all()

    return render_template('ta.html', add_class_form=add_class_form, update_availability_form=update_availability_form, enrolled_classes=enrolled_classes, ta_availability=ta_availability)

@app.route('/logout', methods=['GET', 'POST'])
def logout():

    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)