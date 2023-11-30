from flask import Flask, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SubmitField, IntegerField, BooleanField, SelectField
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired
from flask import request
from wtforms import StringField, SubmitField, validators
from datetime import datetime
from wtforms.fields import HiddenField
from flask import jsonify
from flask import current_app

app = Flask (__name__)

app.config['SECRET_KEY'] = 'oursecretkey'
# setups the database called TASC
# new folder 'instance' will be created in root directory of app file

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TASC.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Added user_type to denote TA & Student
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
    classname = db.Column(db.String(50), nullable=False) 
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


class Scheduled_Appointments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ta_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ta_display_name = db.Column(db.String(50), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_display_name = db.Column(db.String(50), nullable=False)
    appointment_class = db.Column(db.String(50), nullable=False)
    appointment_day = db.Column(db.String(20), nullable=False)
    appointment_start_time = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(200), nullable=True)

class TAAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ta_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    monday_start = db.Column(db.String(10))
    monday_end = db.Column(db.String(10))
    tuesday_start = db.Column(db.String(10))
    tuesday_end = db.Column(db.String(10))
    wednesday_start = db.Column(db.String(10))
    wednesday_end = db.Column(db.String(10))
    thursday_start = db.Column(db.String(10))
    thursday_end = db.Column(db.String(10))
    friday_start = db.Column(db.String(10))
    friday_end = db.Column(db.String(10))

# We may need to add a FlaskForm to collect the message data and store it from the webpage, similar to signup page/user db
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.Float, nullable=False)

def get_time_intervals():
    # Generate time intervals from 8:00 AM to 5:00 PM with 30-minute increments
    intervals = [(f'{hour:02d}:{minute:02d}', f'{hour % 12 or 12:02d}:{minute:02d} {"AM" if hour < 12 else "PM"}') for hour in range(8, 17) for minute in [0, 30]]
    return intervals

class SignupForm(FlaskForm):
    user_type = SelectField('Please select user type:', choices=[('TA', 'TA'), ('Student', 'Student')], validators=[DataRequired()])
    user_name = StringField('Username:', validators=[DataRequired()])
    password = StringField('Password:', validators=[DataRequired()])
    confirm_password = StringField('Confirm your password:', validators=[DataRequired()])
    display_name = StringField('Full Name:', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    user_name = StringField('Username:', validators=[DataRequired()])
    password = StringField('Password:', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Form to let student scehdule an appointment
class StudentAppointmentForm(FlaskForm):
    class_choice = SelectField('Select Class', choices = [], validators=[DataRequired()])
    ta_choice = SelectField('Select TA:', choices = [], validators=[DataRequired()])
    day_choice = SelectField('Select Day', choices=[], validators=[DataRequired()])
    time_choice = SelectField('Select Time', choices=[], validators=[DataRequired()])
    question = TextAreaField('Optional Question to Send')
    submit = SubmitField('Submit')

# Form to let TAs submit/create a class
class AddClassForm(FlaskForm):
    classname = StringField('Class Name', validators=[DataRequired()])
    submit = SubmitField('Add Class')

# Form to let TAs submit their availability
class UpdateAvailabilityForm(FlaskForm):
    available_times = [
        '08:00am', '08:30am', '09:00am', '09:30am', '10:00am',
        '10:30am', '11:00am', '11:30am', '12:00pm', '12:30pm',
        '01:00pm', '01:30pm', '02:00pm', '02:30pm', '03:00pm',
        '03:30pm', '04:00pm', '04:30pm', '05:00pm'
    ]

    # Add "Not Available" option
    choices = [(time, time) for time in available_times]
    choices.append(('not_available', 'Not Available'))

    monday_start = SelectField('Monday Start Time', choices=choices, default='not_available')
    monday_end = SelectField('Monday End Time', choices=choices, default='not_available')

    tuesday_start = SelectField('Tuesday Start Time', choices=choices, default='not_available')
    tuesday_end = SelectField('Tuesday End Time', choices=choices, default='not_available')

    wednesday_start = SelectField('Wednesday Start Time', choices=choices, default='not_available')
    wednesday_end = SelectField('Wednesday End Time', choices=choices, default='not_available')

    thursday_start = SelectField('Thursday Start Time', choices=choices, default='not_available')
    thursday_end = SelectField('Thursday End Time', choices=choices, default='not_available')

    friday_start = SelectField('Friday Start Time', choices=choices, default='not_available')
    friday_end = SelectField('Friday End Time', choices=choices, default='not_available')

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

    # Check if the user is logged in; if not, redirect to login page
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get user information
    user_id = session['user_id']
    user_name = User.query.get(session['user_id']).user_name
    user_type = User.query.get(session['user_id']).user_type
    display_name = User.query.get(session['user_id']).display_name

    # Initialize selected_day
    selected_day = None  
    
    # Create an instance of the StudentAppointmentForm
    form = StudentAppointmentForm()

    # Get a list of unique classes from the database
    available_classes = Class.query.distinct(Class.classname).all()
    class_names = list(set(course.classname for course in available_classes))

    tas_response = []
    time_response = []
    upcoming_appointments= []

    if request.method == 'POST':
        if 'submit_class' in request.form:
            # get the selected class and fetch TAs
            selected_class = request.form.get('class_choice')
            session['class'] = selected_class
            if  selected_class == None:
                no_class = 'Please select a valid class'
                upcoming_appointments = Scheduled_Appointments.query.filter(Scheduled_Appointments.student_id == user_id).all()
                return render_template('student.html', user_name=user_name, user_type=user_type,
                            display_name=display_name, form=form, class_names=class_names, tas_response = tas_response, time_response = time_response, no_class = no_class, upcoming_appointments = upcoming_appointments)
            else:    
                tas_response = get_tas(selected_class)

                # refresh the upcoming appointments
                upcoming_appointments = Scheduled_Appointments.query.filter(Scheduled_Appointments.student_id == user_id).all()
                return render_template('student.html', user_name=user_name, user_type=user_type,
                            display_name=display_name, form=form, class_names=class_names, tas_response = tas_response, time_response = time_response, upcoming_appointments = upcoming_appointments)
            
        elif 'submit_ta_day' in request.form:
            upcoming_appointments = Scheduled_Appointments.query.filter(Scheduled_Appointments.student_id == user_id).all()
            selected_ta = request.form.get('ta_choice')
            session['selected_ta'] = selected_ta
            selected_day = request.form.get('day_choice')
            session['selected_day'] = selected_day
            time_response = get_availability(selected_ta, selected_day)
            if time_response == [['Not Available']]:
                no_times = 'There are no available times for the selected TA and Day. Please try again.'
                return render_template('student.html', user_name=user_name, user_type=user_type,
                            display_name=display_name, form=form, class_names=class_names, tas_response = tas_response, time_response = time_response, selected_ta = selected_ta, selected_day = selected_day, upcoming_appointments = upcoming_appointments, no_times=no_times)
            ta_id =  get_ta_id(selected_ta) # Get ta_id, this will be used for the appoint db table.
            session['ta_id'] = ta_id
            
            return render_template('student.html', user_name=user_name, user_type=user_type,
                            display_name=display_name, form=form, class_names=class_names, tas_response = tas_response, time_response = time_response, selected_ta = selected_ta, selected_day = selected_day, upcoming_appointments = upcoming_appointments)
        
        elif 'submit_appointment' in request.form:
            selected_time = request.form.get('time_choice')
            selected_question = request.form.get('question')

            # Create a new appointment in the database
            appointment = Scheduled_Appointments(
                ta_id=session['ta_id'],
                ta_display_name=session.get('selected_ta'),
                student_id=user_id,
                student_display_name = user_name,
                appointment_class = session['class'],
                appointment_day = session['selected_day'],
                appointment_start_time=selected_time,
                message=selected_question
            )
            db.session.add(appointment)
            db.session.commit()
        
    upcoming_appointments = Scheduled_Appointments.query.filter(Scheduled_Appointments.student_id == user_id).all()
    session['class'] = None
    # Render the student page with class names, selected class, and TAs
    return render_template('student.html', user_name=user_name, user_type=user_type,
                            display_name=display_name, form=form, class_names=class_names, tas_response = tas_response, time_response = time_response, upcoming_appointments = upcoming_appointments)
    
@app.route('/ta', methods=['GET', 'POST'])
def ta():
    add_class_form = AddClassForm()
    update_availability_form = UpdateAvailabilityForm()

    ta_id = session['user_id']    
    print(ta_id)
    # Retrieve TA availability outside the form validation block
    ta_availability = TAAvailability.query.filter_by(ta_id=session['user_id']).first() #here

    if request.method == 'POST':
        print(request.form)
        # handles adding a class
        if add_class_form.validate_on_submit():
            classname = add_class_form.classname.data

            # Create a new class entry
            new_class = Class(classname=classname, ta_id=session['user_id']) #here
    
            try:
                db.session.add(new_class)
                db.session.commit()
                flash(f'Class {classname} added successfully!', 'success')
            except Exception as e:
                print(f"Error committing ta changes: {e}")
                db.session.rollback()

        # handles changing availability
        elif update_availability_form.validate_on_submit():
            # Update availability for the new class
            if ta_availability is None:
                ta_availability = TAAvailability(ta_id=session['user_id']) #here

           # Make a list of times
            available_times = [
                '08:00am', '08:30am', '09:00am', '09:30am', '10:00am',
                '10:30am', '11:00am', '11:30am', '12:00pm', '12:30pm',
                '01:00pm', '01:30pm', '02:00pm', '02:30pm', '03:00pm',
                '03:30pm', '04:00pm', '04:30pm', '05:00pm'
            ]
            
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                start_time = getattr(update_availability_form, f"{day.lower()}_start").data
                end_time = getattr(update_availability_form, f"{day.lower()}_end").data
                
                if start_time and end_time:
                    if start_time == 'not_available' or end_time == 'not_available':
                        setattr(ta_availability, f"{day.lower()}_start", None)
                        setattr(ta_availability, f"{day.lower()}_end", None)
                    else:
                        # finds the index of the start and end times within available_times
                        start_time_index = available_times.index(start_time)
                        end_time_index = available_times.index(end_time)
                        
                        # Sets start time and end time for TA availability
                        if start_time_index < end_time_index:
                            setattr(ta_availability, f"{day.lower()}_start", start_time)
                            setattr(ta_availability, f"{day.lower()}_end", end_time)
                else:
                    # Handle the case where no time is selected
                    setattr(ta_availability, f"{day.lower()}_start", None)
                    setattr(ta_availability, f"{day.lower()}_end", None)

            try:
                db.session.add(ta_availability)
                db.session.commit()
                flash('Availability updated successfully!', 'success')
            except Exception as e:
                print(f"Error committing availability changes: {e}")
                db.session.rollback()
        else:
            print("form validation failed")
            print(update_availability_form.errors)

        return redirect(url_for('ta'))
   
    ta_username = session.get('user_name')
    enrolled_classes = Class.query.filter_by(ta_id=session['user_id']).all() #here

    upcoming_appointments = Scheduled_Appointments.query.filter(Scheduled_Appointments.ta_id == session['user_id']).all()

    return render_template('ta.html', add_class_form=add_class_form, update_availability_form=update_availability_form, enrolled_classes=enrolled_classes, ta_availability=ta_availability, upcoming_appointments = upcoming_appointments)

@app.route('/logout', methods=['GET', 'POST'])
def logout():

    session.clear()
    return redirect(url_for('login'))

def get_ta_id(selected_ta):
    ta = User.query.filter_by(display_name=selected_ta).first()
    # make sure this doesnt return a tuple
    if ta:
        return ta.id
    return None  # Return None if TA is not found

def get_tas(selected_class):
    ta_names = []

    # Query database to get the TA names for the selected class
    # this is a list[] of ta_ids [(1,) , (2,)]
    ta_ids_for_class = Class.query.filter_by(classname=selected_class).with_entities(Class.ta_id).all()

    if ta_ids_for_class:
        for ta_id_tuple in ta_ids_for_class:
            ta_id = ta_id_tuple[0] # Extract the TA id from the tuple
            ta_name = User.query.filter_by(id=ta_id).first().display_name # query the name from User table using ta_id

            if ta_name:
                ta_names.append(ta_name)
            else:
                ta_names.append("No TA found")
                   
        return ta_names
    else:
        return ['GET TAS ERROR']


def get_availability(selected_ta, selected_day):
    selected_ta_id = User.query.filter_by(display_name = selected_ta).first().id
    day_start = (selected_day + "_start").lower()
    day_end = (selected_day + "_end").lower()

    # query db to get availability using selected_ta as the basis. we need to get ta_id
    start_time = TAAvailability.query.filter_by(ta_id=selected_ta_id).with_entities(getattr(TAAvailability, day_start)).first()
    end_time = TAAvailability.query.filter_by(ta_id=selected_ta_id).with_entities(getattr(TAAvailability, day_end)).first()

    timeslots = timesplit([start_time[0], end_time[0]])

    return timeslots


def timesplit(time_slot):
    # time slot is a list of [start_time, end_time]
    available_times = [
        '08:00am', '08:30am', '09:00am', '09:30am', '10:00am',
        '10:30am', '11:00am', '11:30am', '12:00pm', '12:30pm',
        '01:00pm', '01:30pm', '02:00pm', '02:30pm', '03:00pm',
        '03:30pm', '04:00pm', '04:30pm', '05:00pm'
    ]
    current_time = time_slot[0] # start time
    end_time = time_slot[1] # end time

    # Check if start and end times are in the available_times list
    if current_time not in available_times or end_time not in available_times:
        return [['Not Available']]

    start_index = available_times.index(current_time)
    end_index = available_times.index(end_time)

    result = []

    for i in range(start_index, end_index):
        slot_start_time = available_times[i]
        slot_end_time = available_times[i + 1]
        time_slot = f"{slot_start_time} - {slot_end_time}"
        result.append([time_slot])

    return result


@app.route('/test_route', methods=['POST'])
def test_route():
    return jsonify({'message': 'Test route success!'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
