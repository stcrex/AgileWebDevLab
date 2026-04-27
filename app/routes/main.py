from flask import Blueprint, render_template_string

main_bp = Blueprint("main", __name__)


@main_bp.route("/bootstrap")
def bootstrap_status():
    """Stage-1 style sanity page; kept under /bootstrap so / stays the real app entry."""
    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8"/>
            <title>StudySync — bootstrap</title>
        </head>
        <body style="font-family: system-ui, sans-serif; background:#0f172a; color:#f8fafc; padding:40px;">
            <h1>Flask backend reachable</h1>
            <p>Use <a href="/" style="color:#93c5fd;">/</a> for the full lab app (redirects to exams when logged in).</p>
        </body>
        </html>
        """
    )
