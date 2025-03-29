from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    user_fullname = db.Column(db.String(80))
    user_username = db.Column(db.String(30),primary_key=True, unique=True, nullable=False)
    user_password = db.Column(db.String(30), nullable=False)
    user_level = db.Column(db.String(80))
    user_dob = db.Column(db.String(80))

    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    registration_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)

class Admin(db.Model):
    __tablename__ = 'admin'
    admin_name = db.Column(db.String(80), primary_key=True, nullable=False)
    admin_password = db.Column(db.String(80), nullable=False)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    questions = db.relationship('Question', backref='chapter', lazy=True, cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')



class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, default=datetime.utcnow)
    time_duration = db.Column(db.String(10))
    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True,cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True, cascade='all, delete-orphan')

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(30), db.ForeignKey('users.user_username'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    total_scored = db.Column(db.Integer)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(200), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False)
    # Many-to-many relationship with quizzes
    quiz_assignments = db.relationship('QuizQuestion', backref='question', lazy=True, cascade='all, delete-orphan')

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_question'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    question_order = db.Column(db.Integer, default=0) 
