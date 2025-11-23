@echo off
echo Uninstalling old OpenCV versions...
pip uninstall opencv-python opencv-python-headless opencv-contrib-python -y

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Testing OpenCV installation...
python -c "import cv2; print('OpenCV version:', cv2.__version__); print('Has TrackerCSRT:', hasattr(cv2, 'TrackerCSRT_create') or hasattr(cv2.legacy, 'TrackerCSRT_create'))"

echo.
echo Done! Press any key to continue...
pause







