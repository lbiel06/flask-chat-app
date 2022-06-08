from flask_app import app, db, socketio


# Run

if __name__ == '__main__':
    db.create_all()
    socketio.run(app)
