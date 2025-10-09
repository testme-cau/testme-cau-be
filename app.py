"""
Flask application entry point
"""
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Run development server
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )

