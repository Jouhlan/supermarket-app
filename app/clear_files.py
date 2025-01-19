from app import app, db
from app.models import User, Loan, LoanHistory

with app.app_context():
    try:
        # Clear all data from the tables
        db.session.query(User).delete()
        db.session.query(Loan).delete()
        db.session.query(LoanHistory).delete()

        # Reset the autoincrement values manually (if sqlite_sequence does not exist, skip this step)
        try:
            db.session.execute("DELETE FROM sqlite_sequence WHERE name IN ('User', 'Loan', 'LoanHistory')")
        except Exception as e:
            print(f"Skipping autoincrement reset due to error: {e}")

        # Commit the changes
        db.session.commit()
        print("All data cleared successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()
