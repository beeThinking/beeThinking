#!/bin/bash
# Fix bcrypt compatibility issue with Python 3.14

cd /Users/migi/PycharmProjects/BeeThinking

# Activate virtual environment
source venv/bin/activate

# Uninstall passlib
pip uninstall -y passlib

# Upgrade bcrypt
pip install --upgrade bcrypt

# Install all requirements
pip install -r requirements.txt

echo "✅ bcrypt successfully updated!"
echo "Please restart your FastAPI server."

