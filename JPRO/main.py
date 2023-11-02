from flask import Flask, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SubmitField, IntegerField
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired

app = Flask (__name__)

app.config['SECRET_KEY'] = 'oursecretkey'
# setups the database called users
# new folder 'instance' will be created in root directory of app file
# users are stored here
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

# user model with only username and password fields
# unique id needed to store in database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)


class CoffeeItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    inventory = db.Column(db.Integer, nullable=False)

    coffee_item = db.relationship('CartItem', cascade='all')

class Completed_Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False)
    user = db.Column(db.Text, nullable=False)

class CoffeeItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    inventory = IntegerField('Inventory', validators=[DataRequired()])
    submit = SubmitField('Add Item')

class DeleteCoffeeItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Delete Item')

class MyForm(FlaskForm):
    username = StringField('Please enter your username:', validators=[DataRequired()])
    password = StringField('Please enter your password:', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    coffee_item_id = db.Column(db.Integer, db.ForeignKey('coffee_item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    # make cart and coffee items interact with each other
    coffee_item = db.relationship('CoffeeItem', backref='cart_items')

@app.route('/')

def home():

    if 'total' not in session:
        session['total'] = 0

    if 'user_id' not in session:
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('login'))

    coffee_items = CoffeeItem.query.all()
    user = User.query.get(session['user_id']).username
    return render_template('home.html', coffee_items=coffee_items, user=user)

@app.route('/index')

def index():

    if 'total' not in session:
        session['total'] = 0

    if 'user_id' not in session:
        flash('Please log in to view our menu.', 'warning')
        return redirect(url_for('login'))

    coffee_items = CoffeeItem.query.all()
    user = User.query.get(session['user_id']).username
    return render_template('index.html', coffee_items=coffee_items, user=user)

@app.route ('/login', methods=['GET', 'POST'])

def login():

    if 'user_id' not in session:
        user = "notmanager"
    else:
        user = User.query.get(session['user_id']).username

    form = MyForm()  
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()

        # check if username is already taken
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = username.capitalize()
            session['total'] = 0
            return redirect(url_for('home'))
        else:
            # Failed login, show an error message
            # error function in signup page
            error = "Invalid credentials. Please check your username and password."
            return render_template('login.html', form=form, error=error)
    
    return render_template('login.html', form=form, user=user)

@app.route('/auth')

def auth():

    return render_template('auth.html')

@app.route('/cart')

def cart():
    if 'user_id' not in session:
        flash('Please log in to view your cart.', 'warning')
        user = "notmanager"
        return redirect(url_for('login'))
    else: 
        user = User.query.get(session['user_id']).username

    user_id = session['user_id']
    cart_items = CartItem.query.filter_by(user_id=user_id).all()

    # get items in cart
    cart_items_with_info = [(cart_item.coffee_item, cart_item.quantity) for cart_item in cart_items]

    return render_template('cart.html', cart_items=cart_items_with_info, user=user)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])

def add_to_cart(item_id):
    if 'user_id' not in session:
        flash('Please log in to add items to your cart.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    coffee_item = CoffeeItem.query.get(item_id)

    # Check if the item is already in the cart for the user
    # if item already in cart, quantity is increased
    cart_item = CartItem.query.filter_by(user_id=user_id, coffee_item_id=item_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=user_id, coffee_item_id=item_id)
        db.session.add(cart_item)

    session['total'] += coffee_item.price
    db.session.commit()
    flash(f"{coffee_item.name} added to cart.", 'success')
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET','POST'])

def signup():

    form = MyForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        hashed_password = generate_password_hash(password)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = "Username already taken. Please choose a different username."
            return render_template('signup.html', form=form, error=error)
        
        hashed_password = generate_password_hash(password)
        user = User(username=username, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('auth'))

    return render_template('signup.html', form=form)
    

@app.route('/clear_cart', methods=['POST'])

def clear_cart():
    if 'user_id' not in session:
        flash('Please log in to clear your cart.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    CartItem.query.filter_by(user_id=user_id).delete()
    session['total'] = 0
    db.session.commit()

    flash('Your cart has been cleared.', 'success')
    return redirect(url_for('cart'))

@app.route('/submit_order', methods=['GET','POST'])

def submit_order():
    if 'user_id' not in session:
        flash('Please log in to submit your order.', 'warning')
        return redirect(url_for('login'))

    # Create an order record and display on manager page
    user_id = session['user_id']
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    str1 = ""
    cart = []
    for cart_item in cart_items:
        item_name = CoffeeItem.query.filter_by(id=cart_item.coffee_item_id).first()
        item_name.inventory -= cart_item.quantity
        cart.append("[" + item_name.name + ", ")
        cart.append(item_name.description + ", ")
        cart.append("$" + str('{0:.2f}'.format(item_name.price)) + ", ")
        cart.append(str(cart_item.quantity) + "]")
    order = Completed_Order(order=str1.join(cart), total=session['total'], user=User.query.get(user_id).username)
    db.session.add(order)
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    # Display order submit message, clear cart total
    session['total'] = 0
    flash('Order has been placed. Thank you!', 'success')
    return redirect(url_for('cart'))


@app.route('/manager', methods=['GET', 'POST'])

def manager():

    user = User.query.get(session['user_id']).username

    if  User.query.get(session['user_id']).username == "manager":

        # Get all existing coffee items from the database
        coffee_items = CoffeeItem.query.all()
        completed_orders = Completed_Order.query.all()

        form = CoffeeItemForm()
        if form.validate_on_submit():
            name = form.name.data
            description = form.description.data
            price = form.price.data
            inventory = form.inventory.data

            # Check if an item with the provided name already exists, if so, update item with form data
            existing_item = CoffeeItem.query.filter_by(name=name).first()
            if existing_item:
                existing_item.name = name
                existing_item.description = description
                existing_item.price = price
                existing_item.inventory = inventory
                flash(f"{existing_item.name} details updated.", 'success')
                db.session.commit()
                #return redirect(url_for('manager'))

            # If the item does not exist, add it to the database
            else:
                coffee_item = CoffeeItem(name=name, description=description, price=price, inventory=inventory)
                db.session.add(coffee_item)
                db.session.commit()
                flash(f"{coffee_item.name} added to menu.", 'success')

            # After adding a new item, refresh the coffee_items list
            coffee_items = CoffeeItem.query.all()

            return redirect(url_for('manager'))

        return render_template('manager.html', form=form, coffee_items=coffee_items, completed_orders=completed_orders, user=user)
    
    else:
        return redirect(url_for('index'))

@app.route('/delete', methods=['GET','POST'])

def delete():
    # delete form info posts from manager page here
    form = DeleteCoffeeItemForm()

    if form.validate_on_submit():
        name = form.name.data
        
        # Check if an item with the provided name already exists, delete if so
        existing_item = CoffeeItem.query.filter_by(name=name).first()
        if existing_item:
            db.session.delete(existing_item)
            db.session.commit()
            flash(f"{existing_item.name} deleted from menu.", 'success')
        else:
            flash(f"'{name}' does not exist in the menu")
            return redirect(url_for('manager'))
            
    return redirect(url_for('manager'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)