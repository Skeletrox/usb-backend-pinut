
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import subprocess
import json

CONFIG_FILE = '/support_files/res.json'
print 'CONFIG_FILE ' + CONFIG_FILE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print 'BASe_Dir = %s' %(BASE_DIR)
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9%$in^gpdaig@v3or_to&_z(=n)3)$f1mr3hf9e#kespy2ajlo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [subprocess.check_output(" x=\"$(ifconfig wlan0 | grep \"inet \" | awk -F'[: ]+' '{ print $4 }')\";echo $x", stderr = subprocess.STDOUT, shell=True).replace('\n', '')]
print 'ALLOWED HOSTS IS %s' %(ALLOWED_HOSTS)

# Application definition

INSTALLED_APPS = (
    'createuser.apps.CreateuserConfig',
    'backadmin.apps.BackadminConfig',
    'changevars.apps.ChangevarsConfig',
    'changepermissions.apps.ChangepermissionsConfig',
    'changecaptive.apps.ChangecaptiveConfig',
    'ssidmod.apps.SsidmodConfig',
    'fileupload.apps.FileuploadConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'file-upload.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        #'DIRS': ['file-upload/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'file-upload.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db'),
    }
}



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    'file-upload/static',
]

with open(CONFIG_FILE) as res_file:
                json_data = json.load(res_file)
                active_profile = json_data["active_profile"]
                content_root = json_data[active_profile].get("content_root", "")

MEDIA_URL = content_root
print 'MEDIA_URL = ' + MEDIA_URL
MEDIA_ROOT = MEDIA_URL
