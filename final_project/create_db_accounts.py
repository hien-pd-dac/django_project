import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "final_project.settings");
django.setup()

from accounts.models import User

# User.objects.create_user('phuc', 'phuc@gmail.com', 'H1111111')
# User.objects.create_user('hien2', 'hien2@gmail.com', 'H1111111')
# User.objects.create_user('hien3', 'hien3@gmail.com', 'H1111111')
# User.objects.create_user('hien4', 'hien4@gmail.com', 'H1111111')
# User.objects.create_user('hien5', 'hien5@gmail.com', 'H1111111')
# User.objects.create_user('hien6', 'hien6@gmail.com', 'H1111111')
#
# User.objects.create_user('giang3', 'giang3@gmail.com', 'H1111111')
# User.objects.create_user('giang4', 'giang4@gmail.com', 'H1111111')
# User.objects.create_user('giang5', 'giang5@gmail.com', 'H1111111')
# User.objects.create_user('giang6', 'giang6@gmail.com', 'H1111111')


