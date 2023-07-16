import vk_api
from config import user_token, comm_token
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange


class UsersData:
    def __init__(self):
        self.user_token = user_token
        self.vk = vk_api.VkApi(token=self.user_token)
        self.url = 'https://api.vk.com/method/'
        self.params = {'access_token': self.user_token,
                       'v': '5.131'
                       }

    def get_name_sex_bdate_city(self, user_id):
        params = {'user_ids': user_id,
                  'fields': 'sex, bdate, city'
                  }
        resp = self.vk.method('users.get', {**self.params, **params})
        try:
            return resp
        except Exception:
            send_bot.send_msg(user_id, '''сервис временно не работает, попробуйте позже''')
            return '''сервис временно не работает, попробуйте позже'''

    def search_town_id(self, q):
        params = {'q': q}
        resp = self.vk.method('database.getCities', {**self.params, **params})
        if resp['items']:
            return resp['items'][0]['id']
        else:
            return 1

    def get_photo(self, profile_id, user_id):
        params = {'owner_id': profile_id,
                  'album_id': 'profile',
                  'extended': 'likes, comments'
                  }
        resp = self.vk.method('photos.get', {**self.params, **params})
        photos_list = []
        try:
            for item_photo in resp['items']:
                photo_id = item_photo['id']
                sum_likes_comments = item_photo['likes']['count'] + item_photo['comments']['count']
                photos_list.append((photo_id, sum_likes_comments))
            sorted_tuple = sorted(photos_list, key=lambda x: x[1], reverse=True)
            return sorted_tuple[:3]
        except Exception:
            send_bot.send_msg(user_id, '''сервис временно не работает, попробуйте позже''')

    def search_user(self, user_id, search_sex, age, town_id, offset):
        params = {'sex': {search_sex},
                  'age_from': {age},
                  'age_to': {age},
                  'city': town_id,
                  'fields': 'relation',
                  'offset': {offset},
                  'count': 50}
        resp = self.vk.method('users.search', {**self.params, **params})
        try:
            profiles = resp['items']
            users_vk_id = []
            for profile in profiles:
                if profile['is_closed'] == False:
                    users_vk_id.append(str(profile['id']))
            return users_vk_id
        except Exception:
            send_bot.send_msg(user_id, '''сервис временно не работает, попробуйте позже''')

class SendBot:
    def __init__(self):
        self.comm_token = comm_token
        self.vk = vk_api.VkApi(token=self.comm_token)
        self.longpoll = VkLongPoll(self.vk)
        self.params = {'access_token': self.comm_token,
                       'v': '5.131'
                       }

    def send_msg(self, user_id, message=None, user_vk_id=None, photo_id=None):
        params = {'user_id': user_id,
                  'message': message,
                  'attachment': f'photo{user_vk_id}_{photo_id}',
                  'random_id': randrange(10 ** 7)}
        self.vk.method('messages.send', {**self.params, **params})

    def send_but(self, user_id, message, keyboard=None):
        post = {'user_id': user_id,
                'message': message,
                'random_id': randrange(10 ** 7)
                }
        if keyboard != None:
            post['keyboard'] = keyboard.get_keyboard()
        else:
            post = post
        self.vk.method('messages.send', post)


send_bot = SendBot()
user_data = UsersData()