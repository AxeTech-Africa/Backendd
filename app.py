from flask import Flask, request, render_template, redirect, session, url_for, flash,jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import bcrypt
from flask_mail import Mail, Message

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '9f0d9c501596aa967378e7117bf0d296'


# Mail configuration (Updated for Zoho)
app.config['MAIL_SERVER'] = 'smtp.zoho.com'
app.config['MAIL_PORT'] = 587  # Use 587 for TLS, or 465 for SSL
app.config['MAIL_USE_TLS'] = True  # Enable TLS
app.config['MAIL_USERNAME'] = 'brian@axetech.africa'  # Your Zoho email address
app.config['MAIL_PASSWORD'] = 'Khalifawiz1017'  # Your Zoho password or App Password if 2FA is enabled

# File upload settings
app.config['IMAGE_UPLOAD_FOLDER'] = 'static/images'
app.config['VIDEO_UPLOAD_FOLDER'] = 'static/videos'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'mp4', 'mov', 'avi'}
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 1GB limit

# Helper function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

mail = Mail(app)
db = SQLAlchemy(app)
app.secret_key = '9f0d9c501596aa967378e7117bf0d296'
CORS(app, origins=["http://127.0.0.1:5501"], supports_credentials=True)

# Database Model for User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Property model
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    garages = db.Column(db.String(50), nullable=False)
    basement = db.Column(db.String(50), nullable=False)
    video_url = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # Property status: 'pending' or 'approved'
    images = db.Column(db.String(200))

    def __repr__(self):
        return f'<Property {self.title}>'

# Helper function to send email
def send_email(subject, recipient, body):
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient])
    msg.body = body
    mail.send(msg)

# Initialize DB
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        # Redirect to the frontend login page
        return redirect('http://127.0.0.1:5501/login.html')  # Change to the correct path if needed

# Login Route
# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            session['name'] = user.name
            # After successful login, redirect to the frontend index.html
            return redirect('/dashboard')  # Adjust the URL if needed

        else:
            return render_template('login.html', error='Invalid user')

    return render_template('login.html')





@app.route('/check-login')
def check_login():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return jsonify({'logged_in': True, 'name': user.name, 'email': user.email})
    return jsonify({'logged_in': False})







# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)  # Render the dashboard page with user info
    return redirect(url_for('login'))  # Redirect to login page if user is not logged in



@app.route('/logout')
def logout():
    session.pop('email', None)  # Clear the session
    session.pop('name', None)   # Clear the user's name
    session.pop('logged_in', None)  # Clear the logged_in status
    return redirect('http://127.0.0.1:5501/index.html')  # Redirect to index page after logout


@app.route('/add-property', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        # Use .get() for all form fields to avoid KeyError and handle empty fields
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        price = request.form.get('price', '')
        category = request.form.get('category', '')
        property_type = request.form.get('property_type', '')
        address = request.form.get('address', '')
        country = request.form.get('country', '')
        city = request.form.get('city', '')
        size = request.form.get('size', '')
        rooms = request.form.get('rooms', '')
        bedrooms = request.form.get('bedrooms', '')
        bathrooms = request.form.get('bathrooms', '')

        # Handle checkboxes
        garage = request.form.get('garage', '')
        basement = request.form.get('basement', '')
        extra_details = request.form.get('extra_details', '')

        # Handle video URL
        video_url = request.form.get('video', '')

        # Handle amenities (list of selected values)
        amenities = request.form.getlist('amenities')

        # Initialize file_path to None
        file_path = None

        # Handling file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
                file_path = os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename)

        # Save property details to DB
        new_property = Property(
            title=title,
            description=description,
            price=price,
            category=category,
            property_type=property_type,
            address=address,
            country=country,
            city=city,
            size=size,
            rooms=rooms,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            garages=garage,
            basement=basement,
            video_url=video_url,
            images=file_path
        )
        db.session.add(new_property)
        db.session.commit()

        # Send email to admin for approval
        msg = Message('New Property Submission',
                      sender='brian@axetech.africa',  # Update sender email to your Zoho email
                      recipients=['brian@axetech.africa'])  # Update recipient email
        msg.body = f'''
        A new property has been submitted for review:

        Title: {title}
        Description: {description}
        Price: {price}
        Category: {category}
        Property Type: {property_type}
        Address: {address}
        Country: {country}
        City: {city}
        Size: {size} ft²
        Rooms: {rooms}
        Bedrooms: {bedrooms}
        Bathrooms: {bathrooms}
        Garage: {garage if garage else 'Not specified'}
        Basement: {basement if basement else 'Not specified'}
        Extra Details: {extra_details}
        Amenities: {', '.join(amenities) if amenities else 'None'}
        Video URL: {video_url if video_url else 'No video URL provided'}

        Media: {file_path if file_path else 'No media uploaded'}
        '''
        mail.send(msg)

        # Redirect to success page
        return render_template('property-submission-success.html')

    return render_template('add-property.html')

@app.route('/property-submission-success')
def property_submission_success():
    return render_template('property-submission-success.html')






@app.route('/properties')
def properties():
    # Fetch all properties from the database (or with any filters as needed)
    properties = Property.query.filter_by(status='approved').all()
    return render_template('product.html', properties=properties)

@app.route('/product-details/<int:property_id>')
def product_details(property_id):
    # Fetch the property by ID
    property = Property.query.get_or_404(property_id)
    return render_template('product-details.html', property=property)


if __name__ == '__main__':
    app.run(debug=True)
