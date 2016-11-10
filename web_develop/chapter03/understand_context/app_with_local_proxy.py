import random
from flask import Flask, g, render_template
from werkzeug.local import LocalProxy

from ext import db
from users import User

app = Flask(__name__, template_folder='./')
app.config.from_object('config')
db.init_app(app)


def get_current_user():
    users = User.query.all()
    return random.choice(users)
current_user = LocalProxy(get_current_user)


@app.before_first_request
def setup():
    db.drop_all()
    db.create_all()
    fake_users = [
        User('xiaoming', 'xiaoming@mail.com'),
        User('lilei', 'lilei@mail.com'),
        User('admin', 'admin@mail.com'),
    ]
    db.session.add_all(fake_users)
    db.session.commit()


@app.teardown_appcontext
def teardown(exc=None):
    if exc is None:
        db.session.commit()
    else:
        db.session.rollback()
    db.session.remove()
    g.user = None


@app.context_processor
def template_extras():
    return {'enumerate': enumerate, 'current_user': current_user}


@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404


@app.template_filter('capitalize')
def reverset_filter(s):
    return s.capitalize()


@app.route('/users')
def user_view():
    users = User.query.all()
    return render_template('user.html', users=users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
