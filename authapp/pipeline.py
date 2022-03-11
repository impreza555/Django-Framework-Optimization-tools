from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlencode, urlunparse
import requests
from django.utils import timezone
from social_core.exceptions import AuthForbidden
from authapp.models import UserProfile


def save_user_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'vk-oauth2':
        api_url = urlunparse(('https', 'api.vk.com', '/method/users.get', None,
                              urlencode(OrderedDict(fields=','.join(('bdate', 'sex', 'about', 'personal', 'photo_200')),
                                                    access_token=response['access_token'], v='5.131')), None))
        resp = requests.get(api_url)
        if resp.status_code != 200:
            return
        data = resp.json()['response'][0]
        if data['sex']:
            user.userprofile.gender = UserProfile.MALE if data['sex'] == 2 else UserProfile.FEMALE
        if data['about']:
            user.userprofile.aboutMe = data['about']
        if data['bdate']:
            bdate = datetime.strptime(data['bdate'], '%d.%m.%Y').date()
            user.age = timezone.now().date().year - bdate.year
            if user.age < 18:
                user.delete()
                raise AuthForbidden('social_core.backends.vk.VKOAuth2')
        if data['photo_200']:
            photo_link = data['photo_200']
            photo_response = requests.get(photo_link)
            path_photo = f'users_image/{user.pk}.jpg'
            with open(f'media/{path_photo}', 'wb') as photo:
                photo.write(photo_response.content)
            user.image = path_photo
        if data['personal']['langs']:
            user.userprofile.langs = data['personal']['langs'][0] if len(data['personal']['langs'][0]) > 0 else 'EN'
        user.save()
    if backend.name == 'google-oauth2':
        resp = requests.get('https://www.googleapis.com/oauth2/v2/userinfo?access_token=' + response['access_token'])
        if resp.status_code != 200:
            return
        data = resp.json()
        if data['picture']:
            photo_link = data['picture']
            photo_response = requests.get(photo_link)
            path_photo = f'users_image/{user.pk}.jpg'
            with open(f'media/{path_photo}', 'wb') as photo:
                photo.write(photo_response.content)
            user.image = path_photo
        if data['locale']:
            user.userprofile.langs = data['locale'].upper()
        user.save()
    else:
        return
