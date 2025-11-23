#!/bin/bash

echo "========================================"
echo "Installing YOLO and dependencies..."
echo "========================================"
echo ""

echo "Step 1: Installing ultralytics..."
pip install ultralytics>=8.0.0
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install ultralytics"
    exit 1
fi

echo ""
echo "Step 2: Installing PyTorch..."
pip install torch>=2.0.0 torchvision>=0.15.0
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install PyTorch"
    exit 1
fi

echo ""
echo "Step 3: Verifying installation..."
python -c "from ultralytics import YOLO; print('✅ YOLO installed successfully')"
if [ $? -ne 0 ]; then
    echo "ERROR: YOLO verification failed"
    exit 1
fi

python -c "import torch; print('✅ PyTorch version:', torch.__version__)"
if [ $? -ne 0 ]; then
    echo "ERROR: PyTorch verification failed"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ All dependencies installed successfully!"
echo "========================================"
echo ""
echo "You can now run the application with:"
echo "  python app.py"
echo ""





