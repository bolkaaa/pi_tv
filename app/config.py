from os import environ as env


class Config(object):
    # FLASK CONFIGURATION
    SECRET_KEY = env.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = env.get(
        'SQLALCHEMY_DATABASE_URI',
        'sqlite:///db.sqlite'
    )
    BABEL_DEFAULT_LOCALE = 'sk'
    SQLALCHEMY_ECHO = env.get('SQLALCHEMY_ECHO', False)
    SECURITY_PASSWORD_SALT = env.get('SECURITY_PASSWORD_SALT')
    SECURITY_PASSWORD_HASH = env.get('SECURITY_PASSWORD_HASH', 'pbkdf2_sha512')
    ADMIN_EMAIL = env.get('ADMIN_EMAIL')
    ADMIN_PASSWORD = env.get('ADMIN_PASSWORD')
    # UPLOAD CONFIGURATION
    STATIC_FOLDER = env.get('STATIC_FOLDER', 'static')
    MEDIA_FOLDER = env.get('MEDIA_FOLDER', 'media')
    UPLOADS_FOLDER = env.get('UPLOADS_FOLDER', 'uploads')
    LOOPS_FOLDER = env.get('LOOPS_FOLDER', 'loops')
