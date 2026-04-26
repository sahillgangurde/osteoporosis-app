@echo off
echo Installing production dependencies...
pip install -r requirements_prod.txt
echo.
echo Starting Secured Production Server...
python production_app.py
pause
