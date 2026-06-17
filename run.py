from app import create_app
from app.models import db, Expense

# Initialize the application factory
app = create_app()

if __name__ == '__main__':
    # Boot up the local development server
    app.run(debug=True)