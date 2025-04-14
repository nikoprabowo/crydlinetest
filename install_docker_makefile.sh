#!/bin/bash

set -e

echo "🟡 Updating packages..."
sudo apt update && sudo apt upgrade -y

echo "🟡 Installing dependencies..."
sudo apt install -y ca-certificates curl gnupg lsb-release

echo "🟡 Adding Docker GPG key..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "🟡 Adding Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "🟡 Updating repo and installing Docker..."
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "✅ Docker installed successfully!"
docker --version

echo "🟡 Adding current user ($USER) to docker group..."
sudo usermod -aG docker $USER

echo "🟢 Enabling and starting Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

echo "🟡 Installing Make..."
sudo apt install -y make

echo "✅ Make installed successfully!"
make --version

echo "✅ Installation complete. Please logout and login again or run: exec su -l $USER"