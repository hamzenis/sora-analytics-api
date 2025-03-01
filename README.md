# Sora Analytics API


## Installation

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt

# With Service: Automatic deployement as a service using systemd and uvicorn (Recommended)(Needs root access)
./deploy_service.sh

# Without Service: Run the script only with uvicorn
uvicorn api:app --host 0.0.0.0 --port 47474
```

## Endpoints

- GET `/analytics/` - Get all the analytics data

- POST `/analytics/` - Add a new analytics data