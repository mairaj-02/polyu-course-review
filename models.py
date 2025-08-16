from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# This will be initialized in app.py
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    reviews = db.relationship('Review', backref='author', lazy='dynamic')
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), index=True, unique=True)
    name = db.Column(db.String(200))
    department = db.Column(db.String(100))
    category = db.Column(db.String(50))  # CAR, Service Learning, Leadership, Language
    subcategory = db.Column(db.String(50))  # A, M, N, D for CAR; English/Chinese for Language
    language_requirement = db.Column(db.String(50))  # EW/ER, CW/CR, None
    reviews = db.relationship('Review', backref='course', lazy='dynamic')
    
    # CAR specific fields
    car_category = db.Column(db.String(10))  # A, M, N, D
    
    # Service Learning specific fields
    service_location = db.Column(db.String(100))
    
    # Leadership specific fields
    leadership_type = db.Column(db.String(50))  # Tomorrow's Leaders, Tango
    
    # Language specific fields
    language_type = db.Column(db.String(50))  # English, Chinese
    
    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    grade = db.Column(db.String(5))  # A+, A, A-, etc.
    rating = db.Column(db.Integer)  # 1-5 stars
    content = db.Column(db.Text)
    study_load = db.Column(db.Text)
    teacher_review = db.Column(db.Text)
    alternative_teacher = db.Column(db.Text)
    improvement_suggestions = db.Column(db.Text)
    
    # Service Learning specific fields
    weather = db.Column(db.Text)
    living_conditions = db.Column(db.Text)
    service_experience = db.Column(db.Text)
    
    # Leadership and Language specific fields
    better_grade_teachers = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Review {self.id} for Course {self.course_id}>'