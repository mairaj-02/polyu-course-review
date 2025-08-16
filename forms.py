from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ReviewForm(FlaskForm):
    grade = SelectField('Grade Received', choices=[
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'), 
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'),
        ('D+', 'D+'), ('D', 'D'), ('F', 'F')
    ], validators=[DataRequired()])
    rating = IntegerField('Rating (1-5 stars)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    content = TextAreaField('Course Description', validators=[DataRequired(), Length(min=10, max=500)])
    study_load = TextAreaField('Study Load', validators=[DataRequired(), Length(min=10, max=300)])
    teacher_review = TextAreaField('Teacher Review', validators=[DataRequired(), Length(min=10, max=300)])
    alternative_teacher = TextAreaField('Alternative Teacher Recommendations', validators=[Length(max=300)])
    improvement_suggestions = TextAreaField('Improvement Suggestions', validators=[Length(max=300)])
    
    # Service Learning specific fields
    weather = TextAreaField('Weather Conditions', validators=[Length(max=200)])
    living_conditions = TextAreaField('Living Conditions and Food', validators=[Length(max=300)])
    service_experience = TextAreaField('Service Experience', validators=[Length(max=300)])
    
    # Leadership and Language specific fields
    better_grade_teachers = TextAreaField('Teachers Who Give Better Grades', validators=[Length(max=300)])
    
    submit = SubmitField('Submit Review')

class SearchForm(FlaskForm):
    query = StringField('Search Courses', validators=[DataRequired()])
    submit = SubmitField('Search')

class FilterForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('CAR', 'Cluster Area Requirement'),
        ('Service Learning', 'Service Learning'),
        ('Leadership', 'Leadership'),
        ('Language', 'Language and Communication')
    ])
    subcategory = SelectField('Subcategory', choices=[
        ('', 'All Subcategories'),
        ('A', 'A: Human Nature, relation and development'),
        ('M', 'M: Chinese culture and history'),
        ('N', 'N: Culture, Organization, society, and globalization'),
        ('D', 'D: Science, technology and environment'),
        ('English', 'English'),
        ('Chinese', 'Chinese'),
        ('Tomorrow\'s Leaders', 'Tomorrow\'s Leaders'),
        ('Tango', 'Tango')
    ])
    language_requirement = SelectField('Language Requirement', choices=[
        ('', 'Any'),
        ('EW/ER', 'English Reading/Writing'),
        ('CW/CR', 'Chinese Reading/Writing'),
        ('None', 'None')
    ])
    submit = SubmitField('Apply Filters')