from flask import Flask, render_template, request, redirect, url_for
from database import db
from models import Admin
import os
import jinja2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/QuizMaster_23f2003673/database/data.db'
db.init_app(app)
app.app_context().push()
with app.app_context():
    db.create_all()  # This creates all tables defined in your models
    if not Admin.query.first():
        admin = Admin(admin_name='sameerthakur', admin_password='thakur')  # Set your desired credentials
        db.session.add(admin)
        db.session.commit()


app.secret_key ="sameer"
from controllers.default_controllers import *

@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)