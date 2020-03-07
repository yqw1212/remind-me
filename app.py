from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from wtforms import SelectField, SubmitField, TextAreaField, DateTimeField, TextField
from wtforms.validators import DataRequired, Email
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
import time
import _thread
import sys
import os

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.debug = True
app.secret_key = "secret"

app.config.update(
    MAIL_SERVER='smtp.qq.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USE_TLS=False,
    MAIL_USERNAME='953894443@qq.com',
    MAIL_PASSWORD='hvutpzuxrtwhbffe' # 授权码
)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
'''
dev_db = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', dev_db)
SQLALCHEMY_TRACK_MODIFICATIONS = False
'''
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', prefix + os.path.join(app.root_path, 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
mail = Mail(app)

sendor = "953894443@qq.com"


class RemindDataBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(30))
    text = db.Column(db.String(50))
    email = db.Column(db.String(50))


class RemindMe(FlaskForm):
    '''
    remind_time_year = SelectField("年", validators=[DataRequired("请选择")],
                              choices=[(1, 2020), (2, 2021), (3, 2022), (4, 2023), (5, 2024)], default=1, coerce=int)
    remind_time_month = SelectField("月", validators=[DataRequired("请选择")],
                              choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9),
                                       (10, 10), (11, 11), (12, 12)],
                              default=1, coerce=int)
    remind_time_day = SelectField("日", validators=[DataRequired("请选择")],
                              choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10),
                                       (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18),
                                       (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24)],
                              default=1, coerce=int)
    '''
    remind_time = DateTimeField("提醒时间", validators=[DataRequired], format='%Y-%m-%d %H:%M:%S')
    email = TextField("邮箱", validators=[Email])
    content = TextAreaField("事项", validators=[DataRequired])
    submit = SubmitField("提交")


db.create_all()
@app.route('/', methods=["POST", "GET"])
def remind_me():
    form1 = RemindMe()
    date = form1.remind_time.data
    body = form1.content.data
    email = form1.email.data
    '''
    if request.method == "POST":
        date = request.form.get("date")
        date = date.replace("T", " ")
        date = date+":00"
        print(date)
    '''
    if form1.submit.data:
        message = RemindDataBase(time=date, text=body, email=email)
        db.session.add(message)
        db.session.commit()

        _thread.start_new_thread(timer, (date,))
        '''
        while True:
            datetimes = RemindDataBase.query.filter().all()
            for datetim in datetimes:
                da = datetim.time
                nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if nowtime >= da:
                    print(nowtime)
                    print(da+"\n")
                    base = RemindDataBase.query.get(datetim.id)
                    db.session.delete(base)
                    db.session.commit()
                    '''
    return render_template("index.html", form1=form1)


def test(date):
    datetimes = RemindDataBase.query.filter(RemindDataBase.time == str(date)).all()

    for dateti in datetimes:
        da = dateti.time
        email = dateti.email
        text = dateti.text
        nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        send_message(str(email), text)

        base = RemindDataBase.query.get(dateti.id)
        db.session.delete(base)
        db.session.commit()


def timer(date):
    scheduler = BlockingScheduler()
    scheduler.add_job(test, "date", run_date=date, args=[date])
    scheduler.start()


def send_message(recipients, body):
    with app.app_context():
        msg = Message(subject="Remind you", recipients=[recipients], sender=app.config['MAIL_USERNAME'], body=body)
        mail.send(msg)


if __name__ == '__main__':
    app.run()
