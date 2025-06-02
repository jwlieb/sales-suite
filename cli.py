import click
from flask.cli import with_appcontext
from app import db
from app.models import Product, Sale, Report

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    try:
        db.drop_all()
        db.create_all()
        click.echo('Initialized the database.')
    except Exception as e:
        click.echo(f'Error initializing database: {str(e)}')

def init_app(app):
    """Register database commands with the Flask app."""
    app.cli.add_command(init_db_command) 