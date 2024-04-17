#!/usr/bin/env bash

IP_ADDRESS=$(ip route get 1 | awk '{print $NF;exit}')
FRONTEND_PORT=4173
BACKEND_PORT=5001
echo "VITE_BACKEND_URL=http://localhost:$BACKEND_PORT/" > codepics-ui/.env.development
echo "VITE_BACKEND_URL=http://$IP_ADDRESS:$BACKEND_PORT/" > codepics-ui/.env.production

echo "Run:"
echo "source venv/bin/activate"
echo "cd server"
echo "pip install -r requirements.txt"
echo "flask run --host=0.0.0.0 --port=$BACKEND_PORT"
echo
echo "cd codepics-ui && npm run build-only "
echo "npm run preview -- --host=0.0.0.0 --port=$FRONTEND_PORT"
