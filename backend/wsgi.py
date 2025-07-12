from app import create_app
from gevent import monkey
import eventlet
import os

monkey.patch_all()  # For WebSocket support
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run()
