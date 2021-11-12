from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import requests
from ast import literal_eval


db = SQLAlchemy()


class Records(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.SmallInteger, nullable=False)

    def __repr__(self):
        return f'[id:{self.id}, name: {self.name},Predicted age: {self.age}]'


APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agify_data.sqlite3'
db.init_app(APP)


@APP.route('/')
def base():
    return str(Records.query.all())


@APP.route('/no_older_than_40')
def filtered_ages():
    filtered = Records.query.filter(Records.age <= 40).all()
    return str(filtered)


@APP.route('/check_name')
def check_name():
    BASE_URL = 'http://api.agify.io/?name='
    name = request.args['name']
    data = literal_eval(requests.get(BASE_URL + name).text)
    print(name)
    if not Records.query.all():
        last_id = -1
    else:
        last_id = db.session.query(db.func.max(Records.id)).first()[0]

    try:
        rec = Records(id=last_id+1, name=data['name'], age=data['age'])
        db.session.add(rec)
        db.session.commit()
        return f'RECORD ADDED: {rec}'
    except Exception as e:
        return str(e)


@APP.route('/refresh')
def refresh():
    db.drop_all()
    db.create_all()
    return 'db refreshed'


if __name__ == '__main__':
    APP.run()
