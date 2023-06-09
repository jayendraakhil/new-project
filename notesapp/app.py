from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
from threading import Timer
from plyer import notification
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import uuid
import mask
import re
import bcrypt


app = Flask(__name__)
engine = create_engine('sqlite:///project.db', echo=False)
db = sessionmaker(autoflush=False, bind=engine)()
Base = declarative_base()


class Loginn(Base):
     __tablename__ = 'loginn'
     sno = Column(Integer, primary_key=True )
     uuid = Column(String(36), nullable=False)
     email = Column(String(50), nullable=False)
     password = Column(String(200), nullable=False)
     timestamp = Column(String(30), nullable=False)


class Signup(Base):
    __tablename__ = 'signup'
    email = Column(String(50), primary_key=True)
    password = Column(String(200), nullable=False)
    confirm_password=Column(String(200), nullable=False)
    timestamp = Column(String(30), nullable=False)

class Salt(Base):
  __tablename__ = 'salt'
  email = Column(String(50), primary_key=True)
  salt = Column(String(200), nullable=False)

class Contact(Base):
   __tablename__='Contact'
   sno = Column(Integer, primary_key=True)
   name = Column(String(50), nullable=False)
   phone_num = Column(String(10), nullable=False)
   Subject = Column(String(300), nullable=False)
   email = Column(String(50), nullable=False)
   timestamp = Column(String(30), nullable=False)

class Reminder(Base):
    __tablename__ = "Reminder"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    date_and_time = Column(DateTime, nullable=False)

    
class Notes(Base):
    __tablename__="Notes"
    id=Column(Integer,primary_key=True)
    title = Column(String(2000),nullable=False)
    text = Column(String(),nullable=False)
    timestamp = Column(String(30), nullable=False)


@app.route("/")
def home():
    return render_template("index.html")


# @app.route("/index")
# def home():
#     return render_template("index.html")

@app.route("/logout")
def logout():
    return render_template("index.html")

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        Subject = request.form.get('Subject')
        timestamp = str(datetime.now())

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "Invalid email address. Please try again."

        phone_regex = r'^\d{10,12}$'
        if not re.match(phone_regex, phone):
            error = "Phone number must be between 10 and 12 digits."
            return "Invalid Phone Number. Please try again."

        entry = Contact(name=name, phone_num=phone, Subject=Subject, email=email,timestamp=timestamp)
        db.add(entry)
        db.commit()
        return "Contact entry added successfully!"
    return render_template("contact.html")



@app.route("/login_form", methods=['GET', 'POST'])
def logg():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get("password")
        timestamp = str(datetime.now())

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "Invalid email address. Please try again."
        
        uuid_str =str(uuid.uuid5(uuid.NAMESPACE_URL, email))
        # user = Signup.query.filter_by(email=email).first()
        user = db.query(Signup).filter_by(email=email).first()

        if not user:
            return "Invalid username or password"
        hashed = bcrypt.hashpw(password.encode('utf-8'), mask.mask)
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        
            entry = Loginn(uuid=uuid_str, email=email, password=hashed,timestamp=timestamp)
            db.add(entry)  
            db.commit()
            salt_entry = db.query(Salt).filter_by(email=email).first()
     

            if salt_entry:
                salt = salt_entry.salt
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')
                user = db.query(Signup).filter_by(email=email,password=hashed_password).first()

                if user:
                    # data=get_data_from_cloud() #Connect to middleware,
                    # if data:
                    #     update_html()
                    return render_template('index2.html',ans="Logged in successfully.")
                else:
                    return "Invalid username or password"
    return render_template('login_form.html')
    

@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        timestamp = str(datetime.now())

        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
          return "Invalid email address. Please try again."
        
        if password != confirm_password:
            return "Password and Confirm Password do not match. Please try again."
        
        salt = bcrypt.gensalt().decode('utf-8')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')
        
        user = db.query(Signup).filter_by(email=email).first()

        if user:
          return "User already exists. Please log in."
        
        entry = Signup(email=email, password=hashed_password, confirm_password=confirm_password,timestamp=timestamp)
        db.add(entry)
        db.commit()
        
        salt_entry = Salt(email=email, salt=salt)
        db.add(salt_entry)
        db.commit()

        return render_template('login_form.html' ,ans="User signed up successfully.")
    else:
        return render_template('sign_up.html')
    


@app.route("/notes", methods=['GET', 'POST'])
def notest():
    if request.method == 'POST':
        note_Id = request.form.get('noteId')
        title = request.form.get('title')
        text = request.form.get('text')
        timestamp = str(datetime.now())
        # enter = {}

        # entry = Notes(title=title,text=text,timestamp=timestamp)
        note=Notes(title=title,text=text,timestamp=timestamp)


        db.add(note)

        db.commit()
       
        
    notes = db.query(Notes).all()

    return render_template("notestest.html",notes=notes)

@app.route("/notes/delete", methods=['POST'])
def delete_note():
    if request.method == 'POST':
        note_id = request.form.get('noteId')
        note = db.query(Notes).get(note_id)

        if note:
            db.delete(note)
            db.commit()

    return redirect('/notes')



@app.route("/calendar", methods=['GET', 'POST'])
def calendar():
    if request.method == 'POST':
        title = request.form.get('title')
        date_and_time_str = request.form.get('date_and_time')

        if title and date_and_time_str:
            date_and_time = datetime.strptime(date_and_time_str, '%Y-%m-%dT%H:%M')
            new_reminder = Reminder(title=title, date_and_time=date_and_time)
            db.add(new_reminder)
            db.commit()
            schedule_notification(new_reminder)

    reminders = db.query(Reminder).all()
    return render_template('reminder.html', reminders=reminders)
    


def send_notification(title):
    notification.notify(
        title=' Reminder',
        message=f'{title}',
        timeout=900  # Notification timeout in seconds
    )

def schedule_notification(reminder):
    meeting_time = reminder.date_and_time
    current_time = datetime.now()

    if meeting_time > current_time:
        delta = meeting_time - current_time - timedelta(minutes=15)
        seconds = delta.total_seconds()

        if seconds > 0:
            t = Timer(seconds, send_notification, args=[reminder.title])
            t.start()


if __name__ == '__main__':
    with app.app_context():

     Base.metadata.create_all(engine)
     app.run(debug = True)
