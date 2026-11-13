@echo off
echo កំពុងដំឡើងគម្រោង LMS...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
echo ការដំឡើងបានជោគជ័យ! សូមប្រើ run.bat ដើម្បីបើក Server។
pause