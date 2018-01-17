import os

from app import create_app
from flask import render_template, redirect,jsonify
from flasgger import Swagger
from instance.config import app_config

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

@app.errorhandler(405)
def url_not_found(error):
    return jsonify({'message': "Requested URL is invalid"}),405
@app.errorhandler(404)
def content_not_found(error):
    return jsonify({'message': "Requested url is not found"}),404
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'message': "Internal server error"}),500

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


