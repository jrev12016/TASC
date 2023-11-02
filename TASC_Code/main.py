from flask import Flask, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SubmitField, IntegerField
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired

app = Flask (__name__)

app.config['SECRET_KEY'] = 'oursecretkey'
# setups the database called TASC
# new folder 'instance' will be created in root directory of app file

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TASC.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class MyForm(FlaskForm):
    username = StringField('Please enter your username:', validators=[DataRequired()])
    password = StringField('Please enter your password:', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/')

def home():

        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
       
        user = User.query.get(session['user_id']).username
        return render_template('home.html', user=user)

@app.route('/signup', methods=['GET','POST'])

def signup():

    form = MyForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = "Username already taken. Please choose a different username."
            return render_template('signup.html', form=form, error=error)
        
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('auth'))

    return render_template('signup.html', form=form)

@app.route('/auth')

def auth():

    return render_template('auth.html')

@app.route ('/login', methods=['GET', 'POST'])

def login():

    form = MyForm()  
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()

        # check for correct username and password
        if user and password == user.password:
            session['user_id'] = user.id
            session['username'] = username.capitalize()
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