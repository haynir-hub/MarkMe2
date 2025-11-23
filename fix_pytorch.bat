@echo off
echo ========================================
echo Fixing PyTorch DLL issue...
echo ========================================
echo.

echo Step 1: Uninstalling old PyTorch...
pip uninstall torch torchvision -y

echo.
echo Step 2: Reinstalling PyTorch...
pip install torch torchvision

echo.
echo Step 3: Verifying installation...
python -c "import torch; print('✅ PyTorch version:', torch.__version__)"

echo.
echo ========================================
echo Done! Please restart the application.
echo ========================================
pause





