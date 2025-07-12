from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy without an app, it will be initialized later in app.py
db = SQLAlchemy()

class Todo(db.Model):
    """
    Defines the Todo item model for the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return '<Task %r>' % self.id
