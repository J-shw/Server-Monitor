# Flask Server monitor
This is a simple ping monitoring system. A ping request is sent out at the interval desired (60 seconds i the default)
The system tracks which systems are on/offline. 

## Features
- Simple modern UI
- Easy traffic light system
- Historic data is captured (Not yet displayed)
- Login system for adding more servers (Default Username: admin | Password: admin)
- Basic filtering of Online/Offline (Better options are planned)

## Server list page
![Screenshot 2024-09-12 at 10-48-24 Server Monitor](https://github.com/user-attachments/assets/b55856aa-13be-4ccf-ad8d-0f5ad4a71971)


## Login system
![Screenshot 2024-09-12 at 10-48-39 Login](https://github.com/user-attachments/assets/d4763e35-1cae-4ab8-aeb0-8b69bdb59d60)

## Setup

As of now I have not made an installer script.

Please install python [https://www.python.org/]

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
