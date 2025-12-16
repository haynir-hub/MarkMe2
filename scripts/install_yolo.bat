@echo off
echo ========================================
echo Installing YOLO and dependencies...
echo ========================================
echo.

echo Step 1: Installing ultralytics...
pip install ultralytics>=8.0.0
if errorlevel 1 (
    echo ERROR: Failed to install ultralytics
    pause
    exit /b 1
)

echo.
echo Step 2: Installing PyTorch...
pip install torch>=2.0.0 torchvision>=0.15.0
if errorlevel 1 (
    echo ERROR: Failed to install PyTorch
    pause
    exit /b 1
)

echo.
echo Step 3: Verifying installation...
python -c "from ultralytics import YOLO; print('✅ YOLO installed successfully')"
if errorlevel 1 (
    echo ERROR: YOLO verification failed
    pause
    exit /b 1
)

python -c "import torch; print('✅ PyTorch version:', torch.__version__)"
if errorlevel 1 (
    echo ERROR: PyTorch verification failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ All dependencies installed successfully!
echo ========================================
echo.
echo You can now run the application with:
echo   python app.py
echo.
pause





