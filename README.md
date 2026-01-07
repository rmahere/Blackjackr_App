# Blackjackr App

Blackjackr is a full-stack blackjack game built with React, JavaScript, Python,HTML,CSS and Flask.  
Players can log in, play against a dealer, place bets, and experience sound effects for shuffling, winning, and losing. The app works on both desktop and mobile browsers.



## Requirements

- Python 3.9+
- Node.js 18+
- npm
- Windows PowerShell (recommended)


## Backend Setup (Flask API)

Open PowerShell and run:

#powershell
cd blackjackr_fullstack_react_flask_FINAL\backend

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

Copy-Item .env.example .env

python -c "from app import create_app, db; app=create_app(); ctx=app.app_context(); ctx.push(); db.create_all(); ctx.pop()"

python run.py
