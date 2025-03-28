from flask import current_app as app
from flask import render_template, request, redirect, url_for, session, flash, get_flashed_messages
from models import db, Admin, User, Subject, Chapter, QuizQuestions, Quiz, QuizAttempt
from datetime import datetime
import random, string


# ________------------------- HOME PAGE -------------------__________

@app.route('/home', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('user_username')
        password = request.form.get('user_password')
    
        admin = Admin.query.filter_by(admin_name=username, admin_password=password).first()
        if admin:
            session['admin_name'] = username  
            return redirect(url_for('admin_dashboard'))
        
        user = User.query.filter_by(user_username=username, user_password=password).first()
        if user:
            # Update last login time
            user.last_login = datetime.now()
            db.session.commit()
            
            session['user_username'] = username 
            flash('Login successful! Welcome to your Student dashboard.', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Check your username/password again. Please try again.', 'danger') 

    return render_template('home.html')

# _______-------------------> ADMIN DASHBOARD FUNCTIONALITIES <-------------------________

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_name' in session:
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        questions = QuizQuestions.query.filter(QuizQuestions.chapter_id.isnot(None)).all()
        users = User.query.all()
        
        # Get all explicitly created quizzes from the database
        quizzes = Quiz.query.all()
        
        # Filter quizzes if search parameter is provided
        quiz_search = request.args.get('quiz_search', '')
        if quiz_search:
            filtered_quizzes = []
            for quiz in quizzes:
                # Find the chapter name for this quiz
                chapter = Chapter.query.get(quiz.chapter_id)
                if chapter and quiz_search.lower() in chapter.name.lower():
                    filtered_quizzes.append(quiz)
        else:
            filtered_quizzes = quizzes
            
        if session.get('first_admin_login'):
            flash('Admin login successful! Welcome to the admin dashboard.', 'success')
            session['first_admin_login'] = False
            
        return render_template('admin_dashboard.html', 
                              subjects=subjects, 
                              questions=questions,
                              chapters=chapters, 
                              users=users, 
                              quizzes=quizzes,
                              filtered_quizzes=filtered_quizzes,
                              quiz_search=quiz_search)
    else:
        flash('You need to log in first.', 'warning') 
        return redirect(url_for('home'))
    
# (A) CRUD _____ ---- Creating/Editing/Deleting Subjects, Chapters, Questions and Quizzes ---- _____ 

# __ADDING A NEW SUBJECT__
@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))

    if request.method == 'POST':
        subject_name = request.form.get('subject_name')
        subject_desc = request.form.get('subject_desc')
        new_subject = Subject(name=subject_name, desc=subject_desc)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_subject.html')

# __EDITING A SUBJECT__
@app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))
    
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    
    if request.method == 'POST':
        subject_name = request.form.get('subject_name')
        
        if subject_name:
            subject.name = subject_name
            db.session.commit()
            flash('Subject updated successfully!', 'success')
        else:
            flash('Subject name cannot be empty.', 'danger')
        
        return redirect(url_for('edit_subject', subject_id=subject_id))
    
    return render_template('edit_subject.html', subject=subject, chapters=chapters)

# __DELETING A SUBJECT__
@app.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))
    
    try:
        # Get the subject
        subject = Subject.query.get(subject_id)
        
        if subject is None:
            flash('Subject not found.', 'warning')
            return redirect(url_for('admin_dashboard'))
        
        # Delete the subject using SQLAlchemy ORM
        db.session.delete(subject)
        db.session.commit()
        
        flash('Subject and all associated data deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting subject: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

#  __ADDING A NEW CHAPTER UNDER A SUBJECT__
@app.route('/add_chapter/<int:subject_id>', methods=['GET', 'POST'])
def add_chapter(subject_id):
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))

    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        chapter_name = request.form.get('chapter_name')
        new_chapter = Chapter(name=chapter_name, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_chapter.html', subject=subject)

# __EDITING A CHAPTER__
@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        chapter_name = request.form.get('chapter_name')
        
        if chapter_name:
            chapter.name = chapter_name
            db.session.commit()
            flash('Chapter updated successfully!', 'success')
        else:
            flash('Chapter name cannot be empty.', 'danger')
        
        return redirect(url_for('edit_subject', subject_id=chapter.subject_id))
    
    return render_template('edit_chapter.html', chapter=chapter)

# __DELETING A CHAPTER__
@app.route('/delete_chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))
    
    try:
        # Get the chapter
        chapter = Chapter.query.get_or_404(chapter_id)
        subject_id = chapter.subject_id
        
        # Use SQLAlchemy ORM to handle deletion
        db.session.delete(chapter)
        db.session.commit()
        
        flash('Chapter and all associated data deleted successfully!', 'success')
        return redirect(url_for('edit_subject', subject_id=subject_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting chapter: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

#  __ADD QUESTIONS__ 
@app.route('/add_question/<int:chapter_id>', methods=['GET', 'POST'])
def add_question(chapter_id):
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))

    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        question = request.form.get('question')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')

        try:
            # Create the question without linking to a quiz - explicit None
            new_question = QuizQuestions(
                question=question,
                option1=option1,
                option2=option2,
                option3=option3,
                option4=option4,
                correct_option=correct_option,
                chapter_id=chapter_id,
                quiz_id=None  # Explicitly set to None to avoid auto-creation
            )
            db.session.add(new_question)
            db.session.commit()
            
            flash('Question added successfully!', 'success')
            return redirect(url_for('edit_subject', subject_id=chapter.subject_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding question: {str(e)}', 'danger')
            
    return render_template('add_question.html', chapter=chapter)

# Create Quiz - Step 1: Basic Quiz Info
@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))
    
    subjects = Subject.query.all()
    
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        quiz_date = request.form.get('quiz_date')
        hours = request.form.get('hours', 0)
        minutes = request.form.get('minutes', 0)
        
        # Format time duration
        time_duration = f"{int(hours):02d}:{int(minutes):02d}"
        
        try:
            new_quiz = Quiz(
                chapter_id=chapter_id,
                date_of_quiz=datetime.strptime(quiz_date, '%Y-%m-%d'),
                time_duration=time_duration
            )
            
            db.session.add(new_quiz)
            db.session.commit()
            
            flash('Quiz created successfully! Now add questions to it.', 'success')
            return redirect(url_for('add_quiz_questions', quiz_id=new_quiz.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating quiz: {str(e)}', 'danger')
    
    return render_template('create_quiz.html', subjects=subjects)

# Create Quiz - Step 2: Add Questions
@app.route('/add_quiz_questions/<int:quiz_id>', methods=['GET', 'POST'])
def add_quiz_questions(quiz_id):
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))
    
    # Get the quiz
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Get the chapter for this quiz
    chapter = Chapter.query.get_or_404(quiz.chapter_id)
    
    # Get all questions for this chapter
    questions = QuizQuestions.query.filter_by(chapter_id=chapter.id).all()
    
    if request.method == 'POST':
        # Get all selected question IDs from the form
        selected_question_ids = request.form.getlist('question_ids')
        
        try:
            # First, unassign all questions from this quiz
            QuizQuestions.query.filter_by(quiz_id=quiz_id).update({QuizQuestions.quiz_id: None})
            
            # Then assign only the selected questions to this quiz
            if selected_question_ids:
                for q_id in selected_question_ids:
                    # Skip empty strings and only process valid IDs
                    if q_id and q_id.strip():
                        try:
                            question = QuizQuestions.query.get(int(q_id))
                            if question:
                                question.quiz_id = quiz_id
                        except ValueError:
                            # Skip invalid ID values
                            continue
            
            db.session.commit()
            flash('Questions added to quiz successfully!', 'success')
            return redirect(url_for('view_quiz', quiz_id=quiz_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding questions to quiz: {str(e)}', 'danger')
    
    return render_template('add_quiz_questions.html', quiz=quiz, chapter=chapter, questions=questions)

# View Quiz Details
@app.route('/view_quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = None
    if chapter:
        subject = Subject.query.get(chapter.subject_id)
    
    # Get questions for this quiz
    questions = QuizQuestions.query.filter_by(quiz_id=quiz_id).all()
    
    return render_template('view_quiz.html', 
                          quiz=quiz, 
                          chapter=chapter,
                          subject=subject,
                          questions=questions)
# Edit Quiz
@app.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    subjects = Subject.query.all()
    all_chapters = Chapter.query.all()
    
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        quiz_date = request.form.get('quiz_date')
        hours = request.form.get('hours', 0)
        minutes = request.form.get('minutes', 0)
        
        # Format time duration
        time_duration = f"{int(hours):02d}:{int(minutes):02d}"
        
        # Update quiz details
        quiz.chapter_id = chapter_id
        quiz.date_of_quiz = datetime.strptime(quiz_date, '%Y-%m-%d')
        quiz.time_duration = time_duration
        
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('view_quiz', quiz_id=quiz_id))
    
    # Set default date format for the date input
    formatted_date = quiz.date_of_quiz.strftime('%Y-%m-%d')
    
    # Parse hours and minutes from time_duration
    hours, minutes = map(int, quiz.time_duration.split(':'))
    
    return render_template('edit_quiz.html', 
                          quiz=quiz, 
                          subjects=subjects, 
                          all_chapters=all_chapters,
                          formatted_date=formatted_date,
                          hours=hours,
                          minutes=minutes)

# __DELETING A QUIZ__
@app.route('/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))
    
    try:
        # Get the quiz
        quiz = Quiz.query.get_or_404(quiz_id)
        
        # Use SQLAlchemy ORM to handle deletion
        db.session.delete(quiz)
        db.session.commit()
        
        flash('Quiz deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting quiz: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

# (B) ---------______ MANAGING USERS IN ADMIN DASHBOARD ______--------
@app.route('/manage_users')
def manage_users():
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))
    
    # Get all users
    all_users = User.query.all()
    
    # Filter users if search parameter is provided
    user_search = request.args.get('user_search', '')
    if user_search:
        filtered_users = []
        search_term = user_search.lower()
        for user in all_users:
            if (search_term in user.user_username.lower() or 
                search_term in user.user_fullname.lower()):
                filtered_users.append(user)
    else:
        filtered_users = all_users
    
    # Calculate stats for the dashboard
    total_attempts = QuizAttempt.query.count()
    
    # Calculate average score
    attempts = QuizAttempt.query.all()
    if attempts:
        avg_score = round(sum(attempt.total_scored for attempt in attempts) / len(attempts))
    else:
        avg_score = 0
    
    return render_template('manage_users.html', 
                          users=filtered_users,
                          total_attempts=total_attempts,
                          avg_score=avg_score,
                          user_search=user_search)

# DELETE USER
@app.route('/delete_user/<user_id>')
def delete_user(user_id):
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))
    
    user = User.query.get_or_404(user_id)
    
    # Delete user's quiz attempts
    attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    for attempt in attempts:
        db.session.delete(attempt)
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

#  VIEW USER
@app.route('/view_user/<user_id>')
def view_user(user_id):
    if 'admin_name' not in session:
        flash('You need to log in as admin first.', 'warning')
        return redirect(url_for('home'))
    
    user = User.query.get_or_404(user_id)
    attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    
    # Get quiz details for each attempt
    quiz_details = []
    for attempt in attempts:
        quiz = Quiz.query.get(attempt.quiz_id)
        if quiz:
            chapter = Chapter.query.get(quiz.chapter_id)
            chapter_name = chapter.name if chapter else "Unknown Chapter"
            
            quiz_details.append({
                'attempt': attempt,
                'quiz': quiz,
                'chapter_name': chapter_name
            })
    
    return render_template('user_details.html', 
                          user=user, 
                          quiz_details=quiz_details)







# NEW USER REGISTRATION  (perfectly working)
@app.route('/user_regi', methods=['GET', 'POST'])
def user_regi():
    if request.method == 'POST':
        user_username = request.form.get('user_username')
        user_fullname = request.form.get('user_fullname')
        user_dob = request.form.get('user_dob')
        user_level = request.form.get('user_level')
        user_password = request.form.get('user_password')
        existing_user = User.query.filter_by(user_username=user_username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('user_regi'))
    
        new_user = User(user_fullname=user_fullname, user_username=user_username, user_dob=user_dob,user_level=user_level,user_password=user_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('user_regi.html')

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_username' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('home'))
    
    # Get all necessary data
    quizzes = Quiz.query.all()
    chapters = Chapter.query.all()
    subjects = Subject.query.all()
    scores = QuizAttempt.query.filter_by(user_id=session['user_username']).all()
    
    return render_template('user_dashboard.html', 
                          quizzes=quizzes, 
                          chapters=chapters,
                          subjects=subjects,
                          scores=scores)

# LOGOUT ROUTES (perfectly working)
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('Logged out successfully.', 'info') 
    # Check if admin is logged in
    if 'admin_name' in session:
        session.pop('admin_name', None)  # Remove admin_name from session
        flash('Admin logged out successfully.', 'info')  # Flash logout message
    # Check if user is logged in
    elif 'user_username' in session:
        session.pop('user_username', None)  # Remove user_username from session
        flash('User logged out successfully.', 'info')  # Flash logout message
    else:
        flash('You are not logged in.', 'warning')  # Flash warning if no session exists

    return redirect(url_for('home'))  # Redirect to the home page



















#______________________________________________________________



@app.route('/take_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    if 'user_username' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('home'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter = Chapter.query.get(quiz.chapter_id)
    questions = QuizQuestions.query.filter_by(quiz_id=quiz_id).all()
    
    if request.method == 'POST':
        # Calculate score
        total_questions = len(questions)
        if total_questions == 0:
            flash('This quiz has no questions.', 'warning')
            return redirect(url_for('user_dashboard'))
        
        correct_answers = 0
        
        for question in questions:
            answer_key = f'answer_{question.id}'
            user_answer = request.form.get(answer_key)
            
            # Check if the answer exists and matches the correct option
            if user_answer and user_answer == question.correct_option:
                correct_answers += 1
        
        # Calculate percentage score
        score_percentage = int((correct_answers / total_questions) * 100)
        
        # Save the attempt
        try:
            # Make sure user_id is valid
            if not session.get('user_username'):
                flash('User session expired. Please login again.', 'danger')
                return redirect(url_for('home'))
                
            new_attempt = QuizAttempt(
                user_id=session['user_username'],
                quiz_id=quiz_id,
                total_scored=score_percentage,
                time_stamp_of_attempt=datetime.now()
            )
            db.session.add(new_attempt)
            db.session.commit()
            
            # After commit, the new_attempt should have an ID
            # Make explicit check to avoid NoneType error
            if new_attempt and hasattr(new_attempt, 'id') and new_attempt.id:
                flash(f'Quiz submitted successfully! Your score: {score_percentage}%', 'success')
                return redirect(url_for('quiz_result', attempt_id=new_attempt.id))
            else:
                # If for some reason the attempt wasn't properly saved
                flash('Quiz submitted, but result tracking failed. Your score: {score_percentage}%', 'warning')
                return redirect(url_for('user_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting quiz: {str(e)}', 'danger')
            return redirect(url_for('user_dashboard'))
    
    return render_template('take_quiz.html', 
                          quiz=quiz,
                          chapter=chapter,
                          questions=questions)

@app.route('/quiz_result/<int:attempt_id>')
def quiz_result(attempt_id):
    if 'user_username' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('home'))
    
    # Get the attempt or show 404 if not found
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Security check: Make sure the user only sees their own results
    if attempt.user_id != session['user_username']:
        flash('You do not have permission to view this result.', 'danger')
        return redirect(url_for('user_dashboard'))
    
    # Get the quiz with error handling
    quiz = Quiz.query.get(attempt.quiz_id)
    if not quiz:
        flash('Quiz information not found.', 'warning')
        return redirect(url_for('user_dashboard'))
    
    chapters = Chapter.query.all()
    subjects = Subject.query.all()
    
    return render_template('quiz_result.html',
                          attempt=attempt,
                          quiz=quiz,
                          chapters=chapters,
                          subjects=subjects)



# def safe_delete_by_id(model, id_value):
#     """Delete a record directly using SQL, bypassing SQLAlchemy ORM"""
#     table_name = model.__tablename__
#     stmt = f"DELETE FROM {table_name} WHERE id = ?"
#     db.session.execute(stmt, [id_value])

with app.app_context(): 
    db.create_all()
