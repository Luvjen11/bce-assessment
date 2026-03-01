from flask import Blueprint, render_template
error_page = Blueprint("error_page", __name__)

# 404 error
@error_page.errorhandler(404)
def not_found_error(error):
       return render_template('404.html'), 404

# 401 error
@error_page.errorhandler(401)
def un_authorized(error):
       return render_template('401.html'), 401
