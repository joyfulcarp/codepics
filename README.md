# codepics
Locally hosted online board game emulating Codenames: Pictures.

Pictures are not provided and must be placed into a local directory before hosting the server.

## Run

1. `source venv/bin/activate`
2. Launch backend server
  2.1 `cd server`
  2.2 `flask run --port=5001`

## Architecture

A Vue.js + Vite frontend is used for the game interface. A separate Flask backend if used for handling game logic. Communication is done with JSON.
