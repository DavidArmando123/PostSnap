from app import create_app, db
import os

app = create_app()


with app.app_context():
    if not os.path.exists("postsnap.db"):  
        db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
