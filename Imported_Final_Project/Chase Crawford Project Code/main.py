import os
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import redirect
from flask import url_for
from flask import session


basedir = os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)

app.secret_key = 'password'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Dog():
    def __init__(self, Name,Trainability, Energy, Shedding, Grooming, Barking, Size, You_Tube_Link, Wiki_Page, Image):
        self.Name = Name
        self.Trainability = Trainability
        self.Energy = Energy
        self.Shedding = Shedding
        self.Grooming = Grooming
        self.Barking = Barking
        self.Size = Size
        self.You_Tube_Link = You_Tube_Link
        self.Wiki_Page = Wiki_Page
        self.Image = Image
    def __repr__(self):
        return f"Name = {self.Name} Trainability = {self.Trainability} Energy = {self.Energy} Shedding = {self.Shedding} Grooming = {self.Grooming} Barking = {self.Barking} Size = {self.Size} Image ={self.Image}"

German_Sheppard = Dog("German Sheppard","Highly Trainable","Moderate Energy","Moderate Shedding","Once a month","Some barking","Medium","https://www.youtube.com/watch?v=EpAjY_uAAro","https://en.wikipedia.org/wiki/German_Shepherd","https://images.pexels.com/photos/333083/pexels-photo-333083.jpeg")
Poodle = Dog("Poodle","Highly Trainable","High Energy","Low Shedding","Once a month","Very vocal","Medium","https://www.youtube.com/watch?v=74mx2OWM6mE","https://en.wikipedia.org/wiki/Poodle","https://images.pexels.com/photos/951324/pexels-photo-951324.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
Border_Collie = Dog("Border Collie","Highly Trainable","High Energy","Medium Shedding","Once a week","Some barking","Medium","https://www.youtube.com/watch?v=NeqHSKTqffI","https://en.wikipedia.org/wiki/Border_Collie","https://images.pexels.com/photos/3523317/pexels-photo-3523317.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
Dalmatian = Dog("Dalmatian","Moderately Trainable","High Energy","Low Shedding","Once a month","Some barking","Medium","https://www.youtube.com/watch?v=rZ8t4QAUfRI","https://en.wikipedia.org/wiki/Dalmatian_(dog)","https://images.pexels.com/photos/14173436/pexels-photo-14173436.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
Dobermann = Dog("Dobermann","Highly Trainable","High Energy","Low Shedding","Once a month","Some barking","Medium","https://www.youtube.com/watch?v=e00BzdF5LYA","https://en.wikipedia.org/wiki/Dobermann","https://images.pexels.com/photos/11497219/pexels-photo-11497219.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
Golden_Retriever = Dog("Golden Retriever","Highly Trainable","Moderate Energy","High Shedding","Once a week","Some barking","Medium","https://www.youtube.com/watch?v=kI4EbABtJQ0","https://en.wikipedia.org/wiki/Golden_Retriever","https://images.pexels.com/photos/2253275/pexels-photo-2253275.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
Labrador_Retriever = Dog("Labrador Retriever","Highly Trainable","Moderate Energy","Medium Shedding","Once a month","Some barking","Medium","https://www.youtube.com/watch?v=0cj81wHmfXc","https://en.wikipedia.org/wiki/Labrador_Retriever","https://images.pexels.com/photos/1739095/pexels-photo-1739095.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
Siberain_Huskey = Dog("Siberain Huskey","Highly Trainable","High Energy","High Shedding","Once a month","Very vocal","Medium","https://www.youtube.com/watch?v=Quc4i7Dwr1k","https://en.wikipedia.org/wiki/Siberian_Husky","https://images.pexels.com/photos/3715587/pexels-photo-3715587.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
Beagle = Dog("Beagle","Highly Trainable","Moderate Energy","Low Shedding","Once a month","Very vocal","Small","https://www.youtube.com/watch?v=BAf7lcYEXag","https://en.wikipedia.org/wiki/Beagle","https://images.pexels.com/photos/11425353/pexels-photo-11425353.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
Chihuahua = Dog("Chihuahua","Less Trainable","Moderate Energy","Low Shedding","Once a month","Some barking","Small","https://www.youtube.com/watch?v=dHX2xul3WEk","https://en.wikipedia.org/wiki/Chihuahua_(dog)","https://images.pexels.com/photos/1933464/pexels-photo-1933464.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
Great_Dane = Dog("Great Dane","Moderately Trainable","Low Energy","Low Shedding","Once a week","Quiet","Large","https://www.youtube.com/watch?v=XXzZwEauNng","https://en.wikipedia.org/wiki/Great_Dane","https://images.pexels.com/photos/12787369/pexels-photo-12787369.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
Pomeranian = Dog("Pomeranian","Less Trainable","Moderate Energy","High Shedding","Once a day","Quiet","Small","https://www.youtube.com/watch?v=7ZYJGBw0Z5Y","https://en.wikipedia.org/wiki/Pomeranian_dog","https://images.pexels.com/photos/2694561/pexels-photo-2694561.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
Pug = Dog("Pug","Less Trainable","Moderate Energy","Low Shedding","Once a month","Quiet","Small","https://www.youtube.com/watch?v=8Kkrmubsgf8","https://en.wikipedia.org/wiki/Pug","https://images.pexels.com/photos/1851164/pexels-photo-1851164.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
Dachshund = Dog("Dachshund","Less Trainable","Moderate Energy","Low Shedding","Once a month","Quiet","Small","https://www.youtube.com/watch?v=V9AvLqD9p4w","https://en.wikipedia.org/wiki/Dachshund","https://images.pexels.com/photos/1975516/pexels-photo-1975516.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")
dog_list =[German_Sheppard,Poodle,Border_Collie,Dalmatian,Dobermann,Golden_Retriever,Labrador_Retriever,Siberain_Huskey,Beagle,Chihuahua,Great_Dane,Pomeranian,Pug,Dachshund]


class Profile(db.Model):
    __tablename__ = "Profiles"

    email = db.Column(db.Text, primary_key=True)
    password = db.Column(db.Text)
    confirmPassword = db.Column(db.Text)
    firstName = db.Column(db.Text)
    lastName = db.Column(db.Text)
    trainability = db.Column(db.Text, default="")
    energy = db.Column(db.Text, default="")
    shedding = db.Column(db.Text, default="")
    grooming = db.Column(db.Text, default="")
    barking = db.Column(db.Text, default="")
    size = db.Column(db.Text, default="")

    def __init__(self, email, password, confirmPassword, firstName, lastName, trainability="", energy="", shedding="", grooming="", barking="", size=""):  # Corrected attribute name
        self.email = email
        self.password = password
        self.confirmPassword = confirmPassword
        self.firstName = firstName
        self.lastName = lastName
        self.trainability = trainability
        self.energy = energy
        self.shedding = shedding
        self.grooming = grooming
        self.barking = barking
        self.size = size

    def __repr__(self):
        return f"Email: {self.email} Password: {self.password} Confirmed Password: {self.confirmPassword} First Name: {self.firstName} Last Name: {self.lastName} Trainability: {self.trainability} Energy: {self.energy} Shedding: {self.shedding} Grooming: {self.grooming} Barking: {self.barking} Size: {self.size}"

#Account Creation
@app.route('/form',methods=['POST'])
def process_form():
   
    email = request.form['Email'] 
    password = request.form['Password']
    confirmPassword = request.form['ConfirmPassword']
    firstName = request.form['FirstName']
    lastName = request.form['LastName']
    new_profile = Profile(email=email, password=password, confirmPassword=confirmPassword, firstName=firstName, lastName=lastName)
    if password != confirmPassword:
        result = "Password did not match Confirmation Password"
        return render_template('Account_Creation.html', result=result)
    if not email or not password or not confirmPassword or not firstName or not lastName:
        result = "Please fill out all fields"
        return render_template('Account_Creation.html', result=result)
    if password == confirmPassword:
        db.session.add(new_profile)
        db.session.commit()
        result = "Profile has been created!"
        return render_template('Account_Creation.html', result=result)
    
#Singing into Account    
@app.route('/signingIn', methods=['POST'])
def signingIn():
    email = request.form['Email']
    password = request.form['Password']
    profile = Profile.query.filter_by(email=email).first()
    if profile and profile.password == password:
        session['username'] = profile.firstName
        session['username2'] = profile.lastName
        session['username3'] = profile.email
        return redirect(url_for('home'))
    else:
        result = "Invalid email or password, please try again"
        return render_template('Sign_In.html',result=result)
    
#Deletion of Profile
@app.route('/form2', methods=['POST'])
def delete_profile():
    email = request.form['Email']
    password = request.form['Password']
    profile = Profile.query.filter_by(email=email).first()
    if profile and profile.password == password:
        result = "Profile deleted successfully!"
        db.session.delete(profile)
        db.session.commit()
        return render_template('Delete_Profile.html',result=result)
    else:
        result = "Profile was not found"
        return render_template('Delete_Profile.html',result=result)
    



@app.route('/Dog_Form', methods=['POST'])
def update_profile():
    email = session.get('username3')
    trainability = request.form['trainability']
    profile = Profile.query.filter_by(email=email).first()
    if profile:
        if trainability == "Highly Trainable":
            profile.trainability = "Highly Trainable"
            db.session.commit()
            return '',204
        elif trainability == "Moderately Trainable":
            profile.trainability = "Moderately Trainable"
            db.session.commit()
            return '',204
        elif trainability == "Less Trainable":
            profile.trainability = "Less Trainable"
            db.session.commit()
            return '',204
    else:
        return jsonify({"message": "Profile not found!"})
    
@app.route('/Dog_Form2', methods=['POST'])
def update_profile2():
    email = session.get('username3')
    energy = request.form['energy']
    profile2 = Profile.query.filter_by(email=email).first()
    if profile2:
        if energy == "High Energy":
            profile2.energy = "High Energy"
            db.session.commit()
            return '',204
        if energy == "Moderate Energy":
            profile2.energy = "Moderate Energy"
            db.session.commit()
            return '',204
        if energy == "Low Energy":
            profile2.energy = "Low Energy"
            db.session.commit()
            return '',204
    else:
        return jsonify({"message": "Profile not found!"})
    
@app.route('/Dog_Form3', methods=['POST'])
def update_profile3():
    email = session.get('username3')
    energy = request.form['shedding']
    profile3 = Profile.query.filter_by(email=email).first()
    if profile3:
        if energy == "High Shedding":
            profile3.shedding = "High Shedding"
            db.session.commit()
            return '',204
        if energy == "Moderate Shedding":
            profile3.shedding = "Moderate Shedding"
            db.session.commit()
            return '',204
        if energy == "Low Shedding":
            profile3.shedding = "Low Shedding"
            db.session.commit()
            return '',204
    else:
        return jsonify({"message": "Profile not found!"})

@app.route('/Dog_Form4', methods=['POST'])
def update_profile4():
    email = session.get('username3')
    grooming = request.form['grooming']
    profile4 = Profile.query.filter_by(email=email).first()
    if profile4:
        if grooming == "Once a month":
            profile4.grooming = "Once a month"
            db.session.commit()
            return '',204
        if grooming == "Once a week":
            profile4.grooming = "Moderate Shedding"
            db.session.commit()
            return '',204
        if grooming == "Once a day":
            profile4.grooming = "Once a day"
            db.session.commit()
            return '',204
    else:
        return jsonify({"message": "Profile not found!"})

@app.route('/Dog_Form5', methods=['POST'])
def update_profile5():
    email = session.get('username3')
    barking = request.form['barking']
    profile5 = Profile.query.filter_by(email=email).first()
    if profile5:
        if barking == "Very vocal":
            profile5.barking = "Very vocal"
            db.session.commit()
            return '',204
        if barking == "Some barking":
            profile5.barking = "Some barking"
            db.session.commit()
            return '',204
        if barking == "Quiet":
            profile5.barking = "Quiet"
            db.session.commit()
            return '',204
    else:
        return jsonify({"message": "Profile not found!"})

@app.route('/Dog_Form6', methods=['POST'])
def update_profile6():
    email = session.get('username3')
    size = request.form['size']
    profile6 = Profile.query.filter_by(email=email).first()
    if profile6:
        if size == "Large":
            profile6.size = "Large"
            db.session.commit()
            return '',204
        if size == "Medium":
            profile6.size = "Medium"
            db.session.commit()
            return '',204
        if size == "Small":
            profile6.size = "Small"
            db.session.commit()
            return '',204
    else:
        return jsonify({"message": "Profile not found!"})
    
def calculate_your_dogs():
    email = session.get('username3')
    profile = Profile.query.filter_by(email=email).first()
    if not profile:
        return []
    dog_scores = []
    
    for x in dog_list:
        score = 0
        if x.Trainability == profile.trainability:
            score += 1
        if x.Energy == profile.energy:
            score += 1
        if x.Shedding == profile.shedding:
            score += 1
        if x.Grooming == profile.grooming:
            score += 1
        if x.Barking == profile.barking:
            score += 1
        if x.Size == profile.size:
            score += 1
        dog_scores.append((x,score))
    dog_scores.sort(key=lambda x: x[1], reverse=True)
    top_5_dogs = [dog_score[0] for dog_score in dog_scores[:5]]
    return top_5_dogs

@app.route('/dog/<int:dog_index>')
def dog_profile(dog_index):
    if 1 <= dog_index <= len(dog_list):  
        dog = dog_list[dog_index - 1]
        return render_template('Dog_Profile.html', dog=dog)
    else:
        return "Dog was not found"


@app.route('/')
@app.route('/Home.html')
def home():
    top_5_dogs = calculate_your_dogs()
    username = session.get('username')
    username2 = session.get('username2')
    return render_template('Home.html',username=username, username2=username2, top_5_dogs=top_5_dogs)

@app.route('/Dog_Profile.html')
def Dog_Profile():
    return render_template('Dog_Profile.html')

@app.route('/Dog_Listing.html')
def Dog_Listing():
    return render_template('Dog_Listing.html',dog_list=dog_list)

@app.route('/Account_Creation.html')
def Account_Creation():
    email = session.get('email')
    return render_template('Account_Creation.html', email=email)

@app.route('/Sign_In.html')
def sign_in():
    return render_template('Sign_In.html')

@app.route('/Delete_Profile.html')
def Delete_Profile():
    return render_template('Delete_Profile.html')

@app.route('/Account_Result.html')
def account_result():
    return render_template('Account_Result.html')


@app.route('/favicon.ico')
def favicon():
    return '', 404


    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

#Internet Aquired Sources
#The YouTube videos for the dogs ("Dogs 101") were sourced from Animal Planet's youtube channel or from various other youtube channels that sourced Animal Planets videos. For the sake of siteing my sources for college academic graded submission: these vidoes are not mine and I don't claim ownership of them. 
#The Wikipedia pages for the dogs were sourced directly from the Wikipedia website. For the sake of siteing my sources for college academic graded submission: these pages are not mine and I don't claim ownership of them.
#The images of the dogs were sourced from the website Pexels. For the sake of siteing my sources for college academic graded submission: these images are not mine and I don't claim ownership of them.

#Sources
#I was having some problems getting the application to work from the start of the project. Chatgpt suggested that I implement a type of "secret key" to the app. This would be line 16
#I wanted it where after hiting one of the submit buttons in the Home.html page to not send you to any page. Chatgpt gave me suggestions on how to handle this. This would be any lines with: return '',204
#Chatgpt helped me with an idea of sorting the top 5 dogs to be stored into a variable to be displayed on the Home.html page. This would be lines: 262 to 263
#Chatgpt helped me to figure out how to take the list dog_list and have it be proccessed to the Dog_Listing.html page to be displayed on that page. This would be from lines: 266 to 272 and 278
#Chatgpt helped me with understanding how to make it where when a person signs in, every data input will only affect that specific profiles row on the datatable. This would be from lines 319 to 321. Really just how to use the "session" tool. 
