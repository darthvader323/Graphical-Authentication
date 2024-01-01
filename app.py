from flask import Flask, render_template, request, redirect, url_for, jsonify, flash,session
from flask_sqlalchemy import SQLAlchemy
import random
import secrets
import hashlib
import base64
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    account_blocked= db.Column(db.Boolean, default=False) 
    unsuccessful_attempts = db.Column(db.Integer, default=0)
    images = db.relationship('Image', backref='user', lazy=True)
    image_order = db.Column(db.String(255), nullable=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    unique_image_id = db.Column(db.Integer, nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=False)
    content_hash = db.Column(db.String(64), nullable=False)


with app.app_context():
    db.create_all()


user_counters = {}


def get_user_specific_counter(user_id):
    # Marked change: Use user_counters.get(user_id, 1) to get the counter value
    user_counter = user_counters.get(user_id, 1)
    return user_counter

def increment_user_specific_counter(user_id):
    # Marked change: Use get_user_specific_counter(user_id) to get the current counter value
    user_counters[user_id] = get_user_specific_counter(user_id) + 1

def base64_encode(data):
    return base64.b64encode(data).decode('utf-8')


app.jinja_env.filters['base64_encode'] = base64_encode


@app.route('/check_username_availability', methods=['POST'])
def check_username_availability():
    data = request.get_json()
    username = data.get('username')
    if not username: 
        return ("", 204)

    
    user = User.query.filter_by(username=username).first()

    return jsonify({'available': not bool(user)})

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'username' in request.form:
            username = request.form['username']

        
            user = User.query.filter_by(username=username).first()

            if user:
                flash("Username already taken, please choose a different one.")
                return redirect(url_for('register'))

            
            user = User(username=username)
            db.session.add(user)
            db.session.flush()

            
            uploaded_images_count = 0
            uploaded_content_hashes = {image.content_hash for image in user.images}

            for i in range(1, 10):
                image_field = f'image{i}'
                if image_field in request.files:
                    file = request.files[image_field]
                    if file:
                       
                        file_content = file.read()
                        
                        content_hash = hashlib.sha256(file_content).hexdigest()
                        
                        if content_hash in uploaded_content_hashes:
                            flash("Please upload 9 distinct images.")
                            return redirect(url_for('register'))
                        uploaded_content_hashes.add(content_hash)

                        user_specific_counter = get_user_specific_counter(user.id)
                        unique_image_id = int(f'{user.id}{user_specific_counter}')
                        increment_user_specific_counter(user.id)


                        
                        image = Image(image_data=file_content, user=user, unique_image_id=unique_image_id, content_hash=content_hash)
                        db.session.add(image)
                        uploaded_images_count += 1

            if uploaded_images_count < 9:
                flash("Please upload 9 distinct images.")
                return redirect(url_for('register'))

            user.image_order = ''
            db.session.commit()

            return redirect(url_for('arrange_images', username=username))

    return render_template('register.html')
@app.route('/arrange_images/<username>', methods=['GET', 'POST'])
def arrange_images(username):
    user = User.query.filter_by(username=username).first()

    if not user:

        return render_template('register.html', message="User not found")

    if request.method == 'POST':

        ordered_ids = request.form.get('ordered_ids')

        if not ordered_ids:
  
            return render_template('register.html', message="Invalid request")

  
        user.image_order = ordered_ids
        db.session.commit()


        flash("Registration successful")
        return redirect(url_for('register'))

    images = Image.query.filter_by(user_id=user.id).order_by(Image.unique_image_id).all()
    current_order_ids = [str(image.unique_image_id) for image in images]

    return render_template('arrange_images.html', user=user, images=images, current_order_ids=current_order_ids)
@app.route('/signin', methods=['GET', 'POST'])
def signin_page():
    if request.method == 'POST':
        username = request.form.get('username')


        user = User.query.filter_by(username=username).first()

        if user:
 
            if user.account_blocked:
                flash("Account is blocked due to multiple unsuccessful attempts.", 'error')
                return render_template('signin.html')
            session['user_id'] = user.id

     
            return redirect(url_for('signin_images', username=username))
        else:
   
            flash("Invalid username. Please try again.", 'error')

    return render_template('signin.html')

@app.route('/signin_images/<username>', methods=['GET', 'POST'])
def signin_images(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return render_template('register.html', message="User not found")

    images = Image.query.filter_by(user_id=user.id).order_by(Image.unique_image_id).all()
    current_order_ids = [str(image.unique_image_id) for image in images]


    if request.method == 'POST':
        ordered_ids = request.form.get('ordered_ids')

        if not ordered_ids:
            return render_template('register.html', message="Invalid request")

        if ordered_ids == user.image_order:


            user.unsuccessful_attempts = 0
            db.session.commit()
            return redirect(url_for('dashboard', username=username))

        else:
  
            user.unsuccessful_attempts += 1
            db.session.commit()

  
            if user.unsuccessful_attempts >= 4:
                user.account_blocked=True 
                flash("Account blocked due to multiple unsuccessful attempts.", 'error')
                db.session.commit()
                return redirect(url_for('signin_page'))


    
            flash("Invalid image arrangement. Please try again.", 'error')
            
            random.shuffle(images)
            return redirect(url_for('signin_images', username=username))
  
    random.shuffle(images)

    return render_template('signin_images.html', user=user, images=images, current_order_ids=current_order_ids)
@app.route('/dashboard/<username>', methods=['GET'])
def dashboard(username):
    if 'user_id' not in session:
        flash("Unauthorized access. Please sign in first.", 'error')
        return redirect(url_for('signin_page'))
    user = User.query.filter_by(username=username).first()

    if not user:
     
        return render_template('error.html', message="User not found")

    return render_template('dashboard.html', user=user)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    
    flash("Logout successful")
    return redirect(url_for('register'))




if __name__ == '__main__':
    app.run(debug=True)
