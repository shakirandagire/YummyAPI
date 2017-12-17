import os

from app import create_app
from instance.config import app_config

# config_name = os.getenv('APP_SETTINGS')
config_name = os.getenv('FLASK_CONFIG')
# config_name = "development"
app = create_app(config_name)
if __name__ == '__main__':
    app.run()