from app import create_app
from gevent import monkey
import eventlet

monkey.patch_all()  # For WebSocket support
app = create_app()

if __name__ == '__main__':
    app.run()
