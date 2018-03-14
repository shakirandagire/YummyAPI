import os

class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = "DX456#FGNMK8889999666+JKJJVV_HHVGVVBBMN"
    # SQLALCHEMY_DATABASE_URI = 'postgresql://@localhost/flask_api'
    # SQLALCHEMY_DATABASE_URI =os.environ.get('DATABASE_URL')
    if os.environ.get('DATABASE_URL') is None:
        SQLALCHEMY_DATABASE_URI = 'postgresql://@localhost/flask_api'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True

class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://@localhost/test_db'
    DEBUG = True

class StagingConfig(Config):
    """Configurations for Staging."""
    DEBUG = True

class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}