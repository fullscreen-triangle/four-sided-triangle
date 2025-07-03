#!/bin/bash

# Set up the environment
echo "Setting up the environment..."
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit the .env file with your API keys"
fi

# Check if python 3.10 is installed
echo "Checking Python version..."
python_version=$(python --version 2>&1)
if [[ $python_version != *"3.10"* ]]; then
    echo "Warning: You're not using Python 3.10. Current version: $python_version"
    echo "Please consider using Python 3.10 for best compatibility with ML libraries"
fi

# Install dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Verify LLM model path
MODEL_PATH=${MODEL_PATH:-./models}
if [ ! -d "$MODEL_PATH" ]; then
    echo "Warning: Model directory not found at $MODEL_PATH"
    echo "Please make sure the sprint-llm-distilled model is correctly installed"
fi

# Setup frontend
echo "Setting up frontend..."
cd frontend
npm install
cd ..

# Start the application
echo "Starting the application..."
# Start backend in the background
python run_api.py &
BACKEND_PID=$!

# Wait for the backend to start
echo "Waiting for backend to start..."
sleep 5

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Setup trap to kill processes on exit
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM EXIT

echo "Application started!"
echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:3000"
echo "Press Ctrl+C to stop all services"

# Keep the script running
wait
