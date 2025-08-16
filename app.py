from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from models import db, User, Course, Review
from forms import LoginForm, RegistrationForm, ReviewForm, SearchForm, FilterForm
from config import Config
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login = LoginManager(app)
login.login_view = 'login'

# Add configuration for pagination
app.config['COURSES_PER_PAGE'] = 9

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_first_request
def create_tables():
    db.create_all()
    # Create admin user if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='muhammadmairaj02@gmail.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# Helper function to get stats
def get_stats():
    courses_count = Course.query.count()
    reviews_count = Review.query.count()
    users_count = User.query.count()
    
    return {
        'courses_count': courses_count,
        'reviews_count': reviews_count,
        'users_count': users_count
    }

@app.route('/')
@app.route('/index')
def index():
    form = SearchForm()
    filter_form = FilterForm()
    
    # Get stats for the homepage
    stats = get_stats()
    
    # Get all courses for the stats section
    page = request.args.get('page', 1, type=int)
    courses = Course.query.paginate(page=page, per_page=app.config['COURSES_PER_PAGE'], error_out=False)
    
    return render_template('index.html', title='Home', form=form, filter_form=filter_form, 
                          courses=courses, reviews_count=stats['reviews_count'], 
                          users_count=stats['users_count'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/courses')
def courses():
    page = request.args.get('page', 1, type=int)
    courses = Course.query.paginate(page, app.config['COURSES_PER_PAGE'], False)
    
    # Calculate average ratings for each course
    courses_with_ratings = []
    for course in courses.items:
        avg_rating = 0
        if course.reviews.count() > 0:
            avg_rating = db.session.query(func.avg(Review.rating)).filter(Review.course_id == course.id).scalar() or 0
        courses_with_ratings.append({
            'course': course,
            'avg_rating': avg_rating
        })
    
    return render_template('courses.html', title='Courses', courses=courses, courses_with_ratings=courses_with_ratings)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    subcategory = request.args.get('subcategory', '')
    language_requirement = request.args.get('language_requirement', '')
    
    results = Course.query
    
    if query:
        results = results.filter(
            db.or_(
                Course.code.contains(query),
                Course.name.contains(query)
            )
        )
    
    if category:
        results = results.filter(Course.category == category)
    
    if subcategory:
        results = results.filter(Course.subcategory == subcategory)
    
    if language_requirement:
        results = results.filter(Course.language_requirement == language_requirement)
    
    page = request.args.get('page', 1, type=int)
    results = results.paginate(page, app.config['COURSES_PER_PAGE'], False)
    
    # Calculate average ratings for each course
    courses_with_ratings = []
    for course in results.items:
        avg_rating = 0
        if course.reviews.count() > 0:
            avg_rating = db.session.query(func.avg(Review.rating)).filter(Review.course_id == course.id).scalar() or 0
        courses_with_ratings.append({
            'course': course,
            'avg_rating': avg_rating
        })
    
    return render_template('courses.html', title='Search Results', courses=results, 
                          query=query, courses_with_ratings=courses_with_ratings)

@app.route('/course/<int:id>')
def course_detail(id):
    course = Course.query.get_or_404(id)
    reviews = Review.query.filter_by(course_id=id).order_by(Review.timestamp.desc()).all()
    
    # Calculate grade distribution
    grade_counts = {'A+': 0, 'A': 0, 'A-': 0, 'B+': 0, 'B': 0, 'B-': 0, 'C+': 0, 'C': 0, 'C-': 0, 'D+': 0, 'D': 0, 'F': 0}
    for review in reviews:
        if review.grade in grade_counts:
            grade_counts[review.grade] += 1
    
    # Calculate rating distribution
    rating_counts = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
    for review in reviews:
        rating_str = str(review.rating)
        if rating_str in rating_counts:
            rating_counts[rating_str] += 1
    
    return render_template('course_detail.html', title=course.name, course=course, reviews=reviews,
                          grade_counts=grade_counts, rating_counts=rating_counts)

@app.route('/submit_review/<int:course_id>', methods=['GET', 'POST'])
@login_required
def submit_review(course_id):
    course = Course.query.get_or_404(course_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        review = Review(
            course_id=course.id,
            user_id=current_user.id,
            grade=form.grade.data,
            rating=form.rating.data,
            content=form.content.data,
            study_load=form.study_load.data,
            teacher_review=form.teacher_review.data,
            alternative_teacher=form.alternative_teacher.data,
            improvement_suggestions=form.improvement_suggestions.data
        )
        
        # Add category-specific fields
        if course.category == 'Service Learning':
            review.weather = form.weather.data
            review.living_conditions = form.living_conditions.data
            review.service_experience = form.service_experience.data
        elif course.category in ['Leadership', 'Language']:
            review.better_grade_teachers = form.better_grade_teachers.data
        
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted!')
        return redirect(url_for('course_detail', id=course.id))
    
    return render_template('submit_review.html', title='Submit Review', form=form, course=course)

@app.route('/select_course_for_review')
@login_required
def select_course_for_review():
    page = request.args.get('page', 1, type=int)
    courses = Course.query.paginate(page, app.config['COURSES_PER_PAGE'], False)
    
    # Calculate average ratings for each course
    courses_with_ratings = []
    for course in courses.items:
        avg_rating = 0
        if course.reviews.count() > 0:
            avg_rating = db.session.query(func.avg(Review.rating)).filter(Review.course_id == course.id).scalar() or 0
        courses_with_ratings.append({
            'course': course,
            'avg_rating': avg_rating
        })
    
    return render_template('select_course_for_review.html', title='Select Course to Review', 
                          courses=courses, courses_with_ratings=courses_with_ratings)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
    
    courses = Course.query.all()
    stats = get_stats()
    
    return render_template('admin.html', title='Admin Panel', courses=courses, 
                          reviews_count=stats['reviews_count'], users_count=stats['users_count'])

@app.route('/add_course', methods=['POST'])
@login_required
def add_course():
    # Check if the course already exists
    data = request.get_json()
    existing_course = Course.query.filter_by(code=data['code']).first()
    if existing_course:
        return jsonify({'success': False, 'message': 'A course with this code already exists'})
    
    course = Course(
        code=data['code'],
        name=data['name'],
        department=data['department'],
        category=data['category'],
        subcategory=data.get('subcategory', ''),
        language_requirement=data.get('language_requirement', 'None')
    )
    
    # Add category-specific fields
    if data['category'] == 'CAR':
        course.car_category = data.get('car_category', '')
    elif data['category'] == 'Service Learning':
        course.service_location = data.get('service_location', '')
    elif data['category'] == 'Leadership':
        course.leadership_type = data.get('leadership_type', '')
    elif data['category'] == 'Language':
        course.language_type = data.get('language_type', '')
    
    db.session.add(course)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Course added successfully', 'course_id': course.id})

@app.route('/change_admin_password', methods=['POST'])
@login_required
def change_admin_password():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_user.check_password(current_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'})
    
    if len(new_password) < 8:
        return jsonify({'success': False, 'message': 'New password must be at least 8 characters long'})
    
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Password changed successfully'})

if __name__ == '__main__':
    app.run(debug=True)