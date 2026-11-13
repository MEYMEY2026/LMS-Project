\# LMS MCQ System



ប្រព័ន្ធគ្រប់គ្រងការប្រឡងអនឡាញ (Learning Management System) ដែលបង្កើតឡើងដោយ Django។



\## លក្ខណៈពិសេស

\- គ្រប់គ្រងគណនី (Admin, គ្រូ, សិស្ស)

\- បង្កើតសំណួរ (Manual \& Import Excel/CSV)

\- បង្កើតការប្រឡង (Random, Select All, Timer, Auto-Submit)

\- ប្រព័ន្ធជូនដំណឹង (Notification Bell)

\- មើលលទ្ធផលលម្អិត (ត្រូវ/ខុស និងពិន្ទុ)

\- PWA (អាចដំឡើងលើទូរស័ព្ទដៃបាន)



\## របៀបដំឡើង (Installation)

1\. ដំឡើង Python (កំណែ 3.9 ឡើងទៅ)

2\. បង្កើត Virtual Environment: `python -m venv venv`

3\. បើក Virtual Environment: `venv\\Scripts\\activate` (Windows)

4\. ដំឡើង Packages: `pip install -r requirements.txt`

5\. បង្កើត Database: `python manage.py migrate`

6\. បង្កើត Admin: `python manage.py createsuperuser`

7\. បើក Server: `python manage.py runserver`

