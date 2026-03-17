#!/usr/bin/env bash
set -euo pipefail

# -- Config -------------------------------------------------------
SERVER="${DEPLOY_SERVER:?DEPLOY_SERVER env var is required (e.g. deploy@1.2.3.4)}"
APP_DIR="/home/deploy/pm-claw"
REPO_URL="https://github.com/KonstantinKlychkov/pm-claw.git"
BRANCH="main"
SERVICE_NAME="pm-claw"
PYTHON="python3.12"

# -- 1. Clone or update repo -------------------------------------
echo "==> Deploying to ${SERVER}..."

ssh "${SERVER}" bash -s <<REMOTE
set -euo pipefail

echo "-- Repo --"
if [ -d "${APP_DIR}/.git" ]; then
    cd "${APP_DIR}"
    git fetch origin
    git reset --hard "origin/${BRANCH}"
    echo "Repo updated."
else
    git clone -b "${BRANCH}" "${REPO_URL}" "${APP_DIR}"
    echo "Repo cloned."
fi

# -- 2. Virtualenv and dependencies ------------------------------
echo "-- Venv --"
cd "${APP_DIR}"
[ -d venv ] || ${PYTHON} -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "Dependencies installed."

# -- 3. Systemd service -------------------------------------------
echo "-- Systemd --"
sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" > /dev/null <<EOF
[Unit]
Description=PM Claw Bot
After=network.target

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/python src/main.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# -- 4. Start and enable ------------------------------------------
echo "-- Service --"
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"
sleep 3
if sudo systemctl is-active --quiet "${SERVICE_NAME}"; then
    echo "==> Deploy complete. Service is running."
else
    echo "==> ERROR: Service failed to start!"
    sudo systemctl status "${SERVICE_NAME}" --no-pager
    exit 1
fi
REMOTE
