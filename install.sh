#!/usr/bin/env bash

set -e

APP_NAME="schach.breburda.at"
APP_DIR="$(pwd)"
PYTHON_BIN="python3"
VENV_DIR=".venv"
ENV_FILE=".env"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"

echo "Installing ${APP_NAME}..."

# Check Python
if ! command -v ${PYTHON_BIN} >/dev/null 2>&1; then
    echo "Error: python3 not found."
    exit 1
fi

echo "Using Python:"
${PYTHON_BIN} --version

# Create virtual environment
if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating virtual environment..."
    ${PYTHON_BIN} -m venv ${VENV_DIR}
else
    echo "Virtual environment already exists."
fi

# Upgrade pip
echo "Updating pip..."
${VENV_DIR}/bin/python -m pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    ${VENV_DIR}/bin/pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found."
fi

# Create .env
if [ ! -f "${ENV_FILE}" ]; then
    echo "Creating .env..."

    cat > ${ENV_FILE} <<EOF
SECRET_KEY=CHANGE_ME_TO_A_RANDOM_SECRET
EOF

else
    echo ".env already exists."
fi

# Create systemd service
echo "Creating systemd service..."

sudo bash -c "cat > ${SERVICE_FILE}" <<EOF
[Unit]
Description=${APP_NAME}
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/${ENV_FILE}
ExecStart=${APP_DIR}/${VENV_DIR}/bin/python ${APP_DIR}/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload and enable service
echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Enabling service..."
sudo systemctl enable ${APP_NAME}

echo "Starting service..."
sudo systemctl restart ${APP_NAME}

echo
echo "Installation complete."
echo
echo "Check status:"
echo "  sudo systemctl status ${APP_NAME}"