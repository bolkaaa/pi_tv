# -*- coding: utf-8 -*-
from flask import Flask, redirect
from flask_security import current_user, login_required, \
     Security, SQLAlchemyUserDatastore, utils
from flask_admin import Admin
from flask_babelex import Babel

from config import Config
from database import db
from models import Loop, Role, User
from views import LoopModelView, UploadsView, UserAdmin


app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)

db.init_app(app)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
babel = Babel(app)


@babel.localeselector
def get_locale():
    return 'sk'


@app.before_first_request
def before_first_request():
    db.create_all()
    user_datastore.find_or_create_role(
        name='admin', description='Administrator'
    )
    user_datastore.find_or_create_role(
        name='client', description='Client'
    )
    encrypted_password = utils.encrypt_password(
        app.config['ADMIN_PASSWORD']
    )
    if not user_datastore.get_user(app.config['ADMIN_EMAIL']):
        user_datastore.create_user(
            email=app.config['ADMIN_EMAIL'],
            password=encrypted_password
        )
    db.session.commit()
    user_datastore.add_role_to_user(app.config['ADMIN_EMAIL'], 'admin')
    db.session.commit()


# just redirects
@app.route('/admin/')
@app.route('/')
@login_required
def index():
    if current_user.has_role('admin'):
        return redirect("/admin/users", code=302)
    else:
        return redirect("/admin/uploads", code=302)


admin = Admin(
    app, 'pi_tv',
    template_mode='bootstrap3',
    base_template='admin/custom_base.html'
)

admin.add_view(UserAdmin(User, db.session, name='Užívatelia', endpoint='users'))
admin.add_view(UploadsView(name='Galéria', endpoint='uploads'))
admin.add_view(LoopModelView(Loop, db.session, name='Sekvencie', endpoint='loops'))


# if __name__ == "__main__":
#    app.run(debug=True)
