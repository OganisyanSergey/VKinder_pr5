from functions import user_data, send_bot
from vk_api.longpoll import VkEventType
from alchemy_select import create_tables, select_of_table, add_in_table
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from datetime import date

for event in send_bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = str(event.user_id)
        list_data = user_data.get_name_sex_bdate_city(event.user_id)
        keyboard = VkKeyboard()
        keyboard.add_button('Начать поиск', VkKeyboardColor.PRIMARY)
        send_bot.send_but(event.user_id, f'Здравствуйте, {list_data[0]["first_name"]}, для поиска нажмите: Начать поиск', keyboard)
        for event in send_bot.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                offset = 0
                if event.text == "Начать поиск":
                    if list_data[0]['sex'] == 2:
                        search_sex = 1
                    elif list_data[0]['sex'] == 1:
                        search_sex = 2
                    elif list_data[0]['sex'] == 0:
                        send_bot.send_msg(user_id,
                                          'Введите пол человека, которго ищете: 1 (если пол женский), 2 (если мужской)')
                        for event in send_bot.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                if event.text == '1' or '2':
                                    search_sex = int(event.text)
                                break
                    if 'bdate' in list_data[0] and len(list_data[0]['bdate'].split('.')) == 3:
                        birth_date = list_data[0]['bdate'].split('.')
                        birth_year = int(birth_date[2])
                        now_year = date.today().year
                        age = str(now_year - birth_year)
                    else:
                        send_bot.send_msg(user_id, 'Введите возраст человека, которого ищете (например 30)): ')
                        for event in send_bot.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                age = event.text
                            break
                    if 'city' in list_data[0]:
                        town_id = list_data[0]['city']['id']
                    else:
                        send_bot.send_msg(user_id, 'Введите название города для поиска')
                        for event in send_bot.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                town = event.text
                                if 3 <= len(town) <= 15:
                                    town_id = user_data.search_town_id(town)
                                elif len(town) > 15:
                                    town = town[:15]
                                    town_id = user_data.search_town_id(town)
                                elif len(town) < 3:
                                    send_bot.send_msg(user_id, '''Поиск произведен по городу Москва, для корректного поиска 
                                                             укажите ваш город в настройках вашего профиля.''')
                                    town_id = 1
                                break
                    users_vk_id = user_data.search_user(user_id, search_sex, age, town_id, offset)
                    create_tables()
                    while True:
                        if offset >= len(users_vk_id) - 1:
                            users_vk_id = user_data.search_user(user_id, search_sex, age, town_id, offset + 1)
                        for profile_id in users_vk_id:
                            if (user_id, profile_id) not in select_of_table():
                                user_vk_link = 'vk.com/id' + str(profile_id)
                                user_photos = user_data.get_photo(profile_id, user_id)
                                send_bot.send_msg(user_id, user_vk_link)
                                add_in_table(user_id, profile_id)
                                try:
                                    for i in user_photos:
                                        send_bot.send_msg(user_id, None, profile_id, i[0])
                                    keyboard = VkKeyboard()
                                    keyboard.add_button('Далее', VkKeyboardColor.POSITIVE)
                                    send_bot.send_but(event.user_id,
                                                 f'Чтобы получить новую анкету, нажмите: Далее',
                                                 keyboard)
                                except Exception:
                                    break
                                for event in send_bot.longpoll.listen():
                                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                        request = event.text
                                        if request == 'Далее':
                                            offset += 1
                                            break
                            else:
                                continue
