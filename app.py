from flask import Flask, render_template, jsonify, request
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__, 
           template_folder='src/views/templates',
           static_folder='src/views/static')

# Import routes
from views.routes import init_routes

# Initialize routes
init_routes(app)

if __name__ == '__main__':
    print("🚀 Starting BlockyHomework Flask Server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🎨 The beautiful UI will now load with CSS and JS!")
    app.run(debug=True, host='0.0.0.0', port=5000) 