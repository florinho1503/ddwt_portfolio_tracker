from app import app, db

def reset_database():
    """Deletes and recreates the database every time the app runs."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database has been reset!")

if __name__ == '__main__':
    reset_database()  # WARNING: This deletes all data!
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
