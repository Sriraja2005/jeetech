@echo off
call venv\Scripts\activate
python manage.py migrate
echo Migration completed!
pause
