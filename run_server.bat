@echo off
echo Starting Django Development Server...
cd /d "%~dp0"
call myenv\Scripts\activate.bat
python manage.py runserver
pause



