
rm -r ./user/migrations/*
rm -r ./patient/migrations/*



python manage.py makemigrations user patient

