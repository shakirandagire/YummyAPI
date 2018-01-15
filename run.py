import os

from app import create_app
from flask import render_template, redirect,jsonify
from flasgger import Swagger
from instance.config import app_config

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

@app.errorhandler(405)
def url_not_found(error):
    return jsonify({
                    'message': "Requested URL is invalid"}),405

swagger = Swagger(app, template= {"securityDefinitions": {
    "TokenHeader": {
        "type": "apiKey",
        "name":"Authorization",
        "in": "header"
    }
}})

@app.route("/")
def main():
    return redirect('/apidocs')
if __name__ == '__main__':
    app.run()


