"""Command-line helper to refresh the local StudySync UWA Handbook catalogue.

Run from the project root after installing requirements:
    python scripts/import_uwa_handbook.py
"""
from app import create_app
from app.extensions import db
from app.handbook_importer import import_handbook_units

app = create_app()
with app.app_context():
    db.create_all()
    downloaded, inserted = import_handbook_units()
    print(f"Downloaded {downloaded} unit records from UWA search pages.")
    print(f"Inserted {inserted} new subjects into the local catalogue.")
