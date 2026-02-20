#!/bin/bash
set -e

# Update and install build dependencies
apt-get update
apt-get install -y python3 python3-pip python3-venv binutils build-essential \
    qt6-base-dev qt6-base-dev-tools \
    libglib2.0-0 libgl1-mesa-glx libegl1-mesa libxrender1 libxkbcommon-x11-0 \
    libdbus-1-3 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
    libxcb-randr0 libxcb-render-util0 libxcb-shm0 libxcb-util1 libxcb-xfixes0 libxcb-shape0

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Build with PyInstaller
# Ensure src is in python path
export PYTHONPATH=$PYTHONPATH:$(pwd)
pyinstaller --clean --noconfirm --onefile --name C-SORTING \
    --add-data "assets:assets" \
    --windowed \
    src/main.py

# Prepare debian structure
# Clean up potential artifacts from previous runs or local dev
rm -rf debian/usr/bin/*
rm -rf debian/usr/share/applications/*

mkdir -p debian/usr/bin
mkdir -p debian/usr/share/applications
mkdir -p debian/usr/share/icons/hicolor/256x256/apps/

cp dist/C-SORTING debian/usr/bin/
cp assets/icon.png debian/usr/share/icons/hicolor/256x256/apps/c-sorting.png

# Create desktop file
cat <<EOF > debian/usr/share/applications/C-SORTING.desktop
[Desktop Entry]
Name=C-SORTING
Comment=Modern intelligent photo sorting tool
Exec=C-SORTING
Icon=c-sorting
Terminal=false
Type=Application
Categories=Utility;
EOF

# Set permissions
find debian -type d -exec chmod 755 {} \;
find debian -type f -exec chmod 644 {} \;
chmod 755 debian/usr/bin/C-SORTING
chmod 755 debian/DEBIAN/control

# Build the package
dpkg-deb --build debian c-sorting_1.0.8_arm64.deb
