# Flask Server monitor
This is a simple ping/fetch monitoring system. A ping or fetch request is sent out at the interval desired (60 seconds is the default)

The system tracks which systems are on/offline. 

## Features
- Simple modern UI
- Easy traffic light system
- Historic data is captured
- View historic data
- Login system for adding more servers (Default Username: admin | Password: admin)
- Basic filtering of Online/Offline (Better options are planned)
- Supports host names, Ip Addresses and URLs
- Fetch or ping requests

## Server list page
![Screenshot 2024-09-12 at 16-16-59 Server Monitor](https://github.com/user-attachments/assets/c949709b-9402-40fc-83c8-b00d31f34583)

## Data editing & historic data
![Screenshot 2024-09-13 at 16-00-35 Server Monitor](https://github.com/user-attachments/assets/07d973c4-f70c-408c-9b7b-9b0ad0d2b923)


## Login system
![Screenshot 2024-09-12 at 10-48-39 Login](https://github.com/user-attachments/assets/d4763e35-1cae-4ab8-aeb0-8b69bdb59d60)

## Setup

As of now I have not made an installer script.

Please install [python](https://www.python.org/)

Then install using pip:
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- Flask-Login
- Flask-Bcrypt
- Flask-APScheduler
- icmplib
- waitress

for example paste 'pip install flask' into command terminal
