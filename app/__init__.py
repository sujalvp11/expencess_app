from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from collections import defaultdict

# Import the shared db instance and model from your models.py file
from app.models import db, Expense

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'mysecretkey'

    # 1. First, tie the database instance to this specific Flask app
    db.init_app(app)

    # 2. Open the app context context and safely generate tables
    with app.app_context():
        db.create_all()

    CATEGORIES = ['Food', 'Transport', 'Rent', 'Utilities', 'Health']

    def parse_date_or_none(s: str):
        if not s:
            return None  
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            return None
        
        
    @app.route("/")
    def index():
        start_str = (request.args.get("start") or "").strip()
        end_str = (request.args.get("end") or "").strip() 
        selected_category = (request.args.get("category") or "").strip()

        # Parse dates safely
        start_date = parse_date_or_none(start_str)
        end_date = parse_date_or_none(end_str) 

        if start_date and end_date and end_date < start_date:
            flash("End date cannot be before start date", "error")
            start_date = end_date = None
            start_str = end_str = ""

        q = Expense.query
        if start_date:
            q = q.filter(Expense.date >= start_date)
        if end_date:
            q = q.filter(Expense.date <= end_date)
        if selected_category:
            q = q.filter(Expense.category == selected_category)

        expenses = q.order_by(Expense.date.desc(), Expense.id.desc()).all()
        total = round(sum(e.amount for e in expenses), 2) 

        return render_template(
            "index.html",
            categories=CATEGORIES,
            today=date.today().isoformat(),
            expenses=expenses,
            total=total,
            start_str=start_str,
            end_str=end_str,
            selected_category=selected_category,
        )



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

    @app.route("/delete/<int:expense_id>", methods=['POST'])
    def delete(expense_id):
        e = Expense.query.get_or_404(expense_id)
        db.session.delete(e)
        db.session.commit()
        flash("Expense deleted", "success")
        return redirect(url_for("index"))

    return app