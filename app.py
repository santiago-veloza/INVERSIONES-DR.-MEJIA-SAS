import sys
import os


backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app import create_app


if __name__ == '__main__':

    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)