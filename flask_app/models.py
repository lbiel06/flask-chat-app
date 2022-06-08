from sqlalchemy.orm import Query # Remove for production
from . import db


# Flask-SQLAlchemy models

class User(db.Model):
    # Type hint, remove for production
    query: Query
    
    username = db.Column(db.String, primary_key=True)
    password_hash = db.Column(db.String)
    online = db.Column(db.Boolean)

    def __init__(self, username, password_hash) -> None:
        self.username = username
        self.password_hash = password_hash
        self.online = False

    def __repr__(self) -> str:
        return f'<User username={self.username}, password-hash={self.password_hash}>'
    

class Message(db.Model):
    # Type hint, remove for production
    query: Query
    
    mid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_ = db.Column(db.String)
    to = db.Column(db.String)
    text = db.Column(db.String)
    date = db.Column(db.DateTime())

    def __init__(self, from_, to, text, date) -> None:
        self.from_ = from_
        self.to = to
        self.text = text
        self.date = date

    def __repr__(self) -> str:
        return f'<Message mid={self.mid}, to={self.to}, from={self.from_}, text={self.text}, date={self.date}>'
