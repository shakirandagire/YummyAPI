from flask import Blueprint

recipe = Blueprint('recipes',__name__)

from .import views