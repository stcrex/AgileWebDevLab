from flask import Blueprint, render_template_string

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>StudySync</title>
        </head>
        <body style="font-family: Arial; background:#0f172a; color:white; padding:40px;">
            <h1>StudySync Flask App Running</h1>
            <p>The initial Flask backend setup is working.</p>
            <p>Next step: add database models and authentication.</p>
        </body>
        </html>
        """
    )
