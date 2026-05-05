"""Account profile fields editable by the signed-in user (Preferences)."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.services import profile_preferences as pp

bp = Blueprint("preferences", __name__)


@bp.get("/preferences")
@login_required
def preferences_get():
    return render_template(
        "preferences.html",
        user=current_user,
        colours=pp.ALLOWED_AVATAR_COLOURS,
        field_help=pp.FIELD_HELP,
        completeness=pp.profile_completeness_score(current_user),
        summary_lines=pp.profile_summary_lines(current_user),
    )


@bp.post("/preferences")
@login_required
def preferences_post():
    payload = pp.parse_profile_form(request.form)
    errors = pp.validate_profile_payload(payload, current_colour=current_user.avatar_colour)

    if errors.get("full_name"):
        flash(errors["full_name"], "warning")
        return redirect(url_for("preferences.preferences_get"))
    for key in ("uwa_id", "program", "skills", "availability", "bio"):
        if errors.get(key):
            flash(errors[key], "warning")
            return redirect(url_for("preferences.preferences_get"))

    colour = pp.normalise_avatar_colour(
        payload.avatar_colour,
        fallback=current_user.avatar_colour,
    )
    requested = (request.form.get("avatar_colour") or "").strip().lower()
    if requested and requested not in pp.ALLOWED_AVATAR_COLOURS:
        flash("Invalid accent colour; keeping previous value.", "info")

    u = current_user
    pp.apply_payload_to_user(u, payload, colour=colour)
    db.session.commit()
    flash("Preferences saved.", "success")
    return redirect(url_for("preferences.preferences_get"))
