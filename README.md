# Wildlife Detector 🦁

Real-time wildlife detection application using MegaDetector and computer vision, built with Electron and Python.

## ✨ Features
- 🎥 Real-time wildlife detection using MegaDetector v6
- 📸 Multi-camera support
- 🎬 Video recording capability
- 📷 Screenshot functionality
- 🌓 Dark/Light mode interface
- 📊 Real-time detection statistics

## 🚀 Quick Start

### Prerequisites
- Node.js and npm
- Python 3.9+
- Anaconda or Miniconda

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Yash-Shindey/wildlife-detector.git
   cd wildlife-detector

Install Node dependencies
bashCopynpm install

Set up Python environment
bashCopy# Create conda environment
conda create -n wildlife-env python=3.9
conda activate wildlife-env

# Install required packages
pip install opencv-python
pip install torch torchvision torchaudio
pip install supervision
pip install pillow
pip install transformers

Run the application
bashCopynpm start


💡 Usage
FeatureDescriptionSwitch CameraToggle between available camerasStart RecordingCapture video with detection overlaysTake ScreenshotCapture the current frameDark/Light ModeToggle using moon/sun iconStats PanelView real-time FPS and detection countsDetection LogHistory of all detections
🛠️ Technical Details
Project Structure
Copywildlife-detector/
├── config/
│   └── Info.plist
├── public/
│   └── index.html
├── src/
│   ├── detector.py      # Main detection logic
│   ├── main.js          # Electron main process
│   └── models/          # MegaDetector models
├── recordings/          # Saved recordings
└── screenshots/         # Saved screenshots
Model Information
This application uses MegaDetector v6 from Microsoft's CameraTraps repository for wildlife detection, combined with a species classifier for more detailed animal identification.
System Requirements

OS: Windows/macOS/Linux
RAM: 4GB minimum (8GB recommended)
Storage: 500MB for installation
Camera: Built-in or USB webcam

📋 Environment Setup
Detailed Python Setup

Create and activate environment
bashCopyconda create -n wildlife-env python=3.9
conda activate wildlife-env

Install core packages
bashCopy# CPU Version
pip install torch torchvision torchaudio
pip install opencv-python supervision pillow transformers

# GPU Version (if NVIDIA GPU available)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118


Verification Steps
pythonCopy# Test your installation with this Python code
import cv2
import torch
from PIL import Image
from transformers import pipeline

# Test camera
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    print("Camera access successful")
cap.release()

# Test PyTorch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
Common Issues
Camera Access

Ensure camera permissions are granted
Close other applications using the camera
Try different camera indices if multiple cameras exist
On macOS, grant terminal camera permissions

PyTorch Installation

Match CUDA version with PyTorch installation for GPU support
CPU version works on all systems but may be slower
For M1/M2 Macs, use the default PyTorch installation

Common Error Solutions

Camera not found
bashCopy# Try different camera indices
cv2.VideoCapture(1)  # or 2, 3, etc.

CUDA not found
bashCopy# Check CUDA installation
nvidia-smi
# Install correct PyTorch version


🔧 Development
Building from Source
bashCopy# Install development dependencies
npm install --save-dev electron

# Run in development mode
npm run dev

# Build for your platform
npm run build
Debug Mode

Press Cmd+Option+I (Mac) or Ctrl+Shift+I (Windows/Linux) to open DevTools
Check terminal for Python backend logs
See browser console for frontend logs

🤝 Contributing
Contributions are welcome! Here's how you can help:

Fork the repository
Create a feature branch
bashCopygit checkout -b feature/AmazingFeature

Commit your changes
bashCopygit commit -m 'Add some AmazingFeature'

Push to the branch
bashCopygit push origin feature/AmazingFeature

Open a Pull Request

📝 License
This project uses the MegaDetector model from Microsoft's CameraTraps repository. See their repository for license details.
🙏 Credits

MegaDetector model from Microsoft's CameraTraps repository
Built using Electron and Python
Detection powered by PyTorch

📚 Additional Resources

Electron Documentation
MegaDetector Documentation
PyTorch Documentation

