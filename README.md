# Visual Authentication System with Graphical Passwords
Users upload nine distinct images during registration, arranging them usng drag and drop in a specific order to create a unique graphical password. Login requires arranging in correct order. After four 
unsuccessful attempts, the account is automatically blocked, ensuring security with a user-friendly interface.
## Features :-
### • Image-based Authentication: 
Users upload nine distinct images during registration, creating a 
unique graphical password by arranging them in a specific order.
### • Use of database:
Use of SQLite to store images and their correct order for authentication.
### • Randomized images:
During login, the system presents the user's images in a 
randomized order, requiring the correct arrangement for authentication.
### • Security Measures: 
An account-blocking mechanism implementation such that after four 
unsuccessful login attempts account gets blocked.
### • User-Friendly Interface:
An intuitive interface for both registration and login processes to 
ensure a positive user experience.
## Technology stack :-
o Python(for backend)  
o Framework-: flask   
o SQLite for database  
o HTML,JavaScript (frontend)  
## How to Use:
### Registration:
• Provide a unique username.  
• Upload and arrange nine distinct images.  
• Save the registration information.  
### Login:
• Enter the registered username.  
• Arrange the displayed images in the correct order to authenticate.  
### Account Security:
• Images are shown in random order and after every incorrect arrangement they get randomized.  
• Account blocking after four consecutive unsuccessful login attempts
## Installation
• Download the repository from the link https://github.com/darthvader323/Graphical-Authentication.git  
• Make sure to install python,flask and SQLAlchemy.  
• Run app.py and go to http://localhost:5000.
