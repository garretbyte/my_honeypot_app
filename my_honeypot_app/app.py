import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import requests  # For geolocation API

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Set up general logging for Flask
logging.basicConfig(filename='honeypot.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Set up a dedicated logger for honeypot clicks
honeypot_logger = logging.getLogger('honeypot')
honeypot_logger.setLevel(logging.INFO)

# Create a file handler for honeypot logs
honeypot_handler = logging.FileHandler('honeypot_clicks.log')
honeypot_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

# Add the handler to the honeypot logger
honeypot_logger.addHandler(honeypot_handler)

@app.route('/')
def home():
    return render_template('home.html')

# Store users and their passwords
users = {
    'admin': 'password',  # Example user
    'user1': 'password123',
    'user2': 'securepass'
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validate credentials
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username  # Track the logged-in user
            flash(f'Welcome, {username}!')
            return redirect(url_for('honeypot'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/log_click')
def log_click():
    # Get the user's IP address
    user_ip = request.remote_addr

    # Fetch geolocation data for the IP address
    try:
        response = requests.get(f'https://ipapi.co/{user_ip}/json/')
        if response.status_code == 200:
            geo_data = response.json()
            latitude = geo_data.get('latitude', 'N/A')
            longitude = geo_data.get('longitude', 'N/A')
        else:
            latitude, longitude = 'N/A', 'N/A'
    except Exception:
        latitude, longitude = 'N/A', 'N/A'

    # Log the IP address and coordinates to the honeypot log
    honeypot_logger.info(f"IP: {user_ip}, Latitude: {latitude}, Longitude: {longitude}")

    # Redirect back to the honeypot page
    return redirect(url_for('honeypot'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/honeypot')
def honeypot():
    if not session.get('logged_in'):
        flash('Unauthorized access detected!')
        return redirect(url_for('login'))
    return render_template('honeypot.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
