from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date

# Import the shared db instance and model from your models.py file
from app.models import db, Expense

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
    app.config['SECRET_KEY'] = 'mysecretkey'

    # 1. First, tie the database instance to this specific Flask app
    db.init_app(app)

    # 2. Open the app context context and safely generate tables
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return render_template('index.html')

    @app.route("/add", methods=['POST'])
    def add():
        description = (request.form.get("description") or "").strip()
        amount_str = (request.form.get("amount") or "").strip()
        category = (request.form.get("category") or "").strip()
        date_str = (request.form.get("date") or "").strip()

        if not description or not amount_str or not category:
            flash("Please fill description, amount, and category", "error")
            return redirect(url_for("index"))
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Amount must be a positive number", "error")
            return redirect(url_for("index"))

        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
        except ValueError:
            d = date.today()
            
        e = Expense(description=description, amount=amount, category=category, date=d)
        db.session.add(e)
        db.session.commit()
            
        flash("Expense added", "success")
        return redirect(url_for("index"))

    return app