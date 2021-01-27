import requests
import time
import os
import shutil
import datetime

today = datetime.datetime.today().strftime("%Y-%m-%d-%S")
my_path = f'C:/{today}/'
ya_disk_api = input("Введите Ваш Яндекс API token: ")
token = input("Введите Ваш VK token: ")

# with open('token.txt', 'r') as t, open('Ya_disk_api.txt', 'r') as y:
#     token = t.read().strip()
#     ya_disk_api = y.read().strip()


class VkSaver:
    def __init__(self, owner_id=None):
        self.token = token
        self.url = 'http://api.vk.com/method/'
        self.owner_id = owner_id
        self.version = '5.126'
        self.photo_stock = {}
        self.albums_list = {}
        self.my_path = my_path
        self.params = {
            'access_token': self.token,
            'v': self.version,
        }
        if owner_id is None:
            self.owner_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']

    def get_albums(self, owner_id=None):
        """find all owner photo albums"""
        if id is None:
            owner_id = self.owner_id
        album_url = self.url + 'photos.getAlbums'
        album_params = {
            'user_id': owner_id,
        }
        response = requests.get(album_url, params={**self.params, **album_params}).json()['response']
        time.sleep(0.3)
        count_albums = response['count']
        print("Количество альбомов = ", count_albums)
        for items in response['items']:
            self.albums_list[str(items['id'])] = items['title']
        for album_id, name in self.albums_list.items():
            print(f"{album_id} - {name}")
        # print(self.albums_list)
        return self.albums_list

    def get_photo(self, user_id=None, album_id=None):
        if user_id is None:
            user_id = self.owner_id
        if album_id is None:
            album_id = 'profile'
        print("Идёт подсчет количества фотографий в альбоме...")
        gp_params = {
            'user_id': user_id,
            'extended': 1,
            'photo_sizes': 1,
            'album_id': album_id
        }
        response = requests.get(self.url + 'photos.get', params={**self.params, **gp_params}).json()['response']
        time.sleep(0.3)
        count_photos = response['count']
        for items in response['items']:
            self.photo_stock[items['id']] = [items['likes']['count'], items['sizes'][-1]['url']]
            time.sleep(0.3)
        print(f"В альбоме {count_photos} фото")
        # print(self.photo_stock)
        return self.photo_stock

    def save_photo(self, load_count: int):
        print("\nЗагружаем во временную папку")
        i = 0
        photo_for_load = dict()
        try:
            os.mkdir(self.my_path)
        except FileExistsError:
            self.my_path = self.my_path.rstrip('/') + '-1/'  # work directory
            my_path = self.my_path.rstrip('/') + '-1/'  # work directory
            os.mkdir(self.my_path)
        for photo, url in self.photo_stock.items():
            if i < load_count and i <= len(self.photo_stock):
                filename = url[1].split('/')[-1].split('?')[0]
                photo_for_load[filename] = url[1]
                i += 1
        count = 1
        part_load = len(photo_for_load) / 10
        percent = round(100 / len(photo_for_load))
        remains = 100 - (len(photo_for_load) * percent)
        for name, url in photo_for_load.items():
            file_path = os.path.join(self.my_path, name)
            part = int(count / part_load)
            download_view = round(count * percent + remains)
            r = requests.get(url, allow_redirects=True).content
            with open(file_path, 'wb') as f:
                f.write(r)
            print(f"[{count} / {len(photo_for_load)}] {'##' * part + '--' * (10 - part)} {download_view} % || {name}\r")
            time.sleep(.1)
            count += 1
        return "all photo downloaded"


class YaUploader:
    def __init__(self):
        self.headers = {"Authorization": f"OAuth {ya_disk_api}"}
        self.file_path = my_path

    def upload(self, dir_path=None):
        """Метод загруджает файлы из папки на яндекс диск"""
        if dir_path is None:
            dir_path = self.file_path
        dir_name = dir_path.split('/')[1]
        contents = []
        print("\nЗагружаем на Yandex disk")
        for item in os.walk(dir_path):
            contents.append(item)
        # print(contents)
        if contents:
            requests.put("https://cloud-api.yandex.net/v1/disk/resources",
                         params={"path": f"{dir_name}"},
                         headers=self.headers
                         )
            for path, dirs, files in contents:
                count = 1
                part_way = len(files) / 10
                percent = round(100 / len(files))
                ost = 100 - (len(files) * percent)
                for elem in files:
                    try:
                        resp = requests.get(
                            "https://cloud-api.yandex.net/v1/disk/resources/upload",
                            params={"path": f"{dir_name}/{elem}"},
                            headers=self.headers
                        )
                        href = resp.json()["href"]
                    except KeyError:
                        resp = requests.get(
                            "https://cloud-api.yandex.net/v1/disk/resources/upload",
                            params={"path": f"{dir_name}/{elem + 'copy'}"},
                            headers=self.headers
                        )
                        href = resp.json()["href"]
                    with open(f"{dir_path}\\{elem}", "rb") as f:
                        requests.put(href, files={"file": f})
                        part = int(count / part_way)
                        status = round(count * percent + ost)
                        print(f"[{count} / {len(files)}] {'##' * part + '--' * (10 - part)} {status} % || {elem}\r")
                        time.sleep(.1)
                        count += 1
                complete = '\nDownload is complete'

        if not contents:
            resp = requests.get(
                "https://cloud-api.yandex.net/v1/disk/resources/upload",
                params={"path": f"{dir_name}"},
                headers=self.headers
            )
            href = resp.json()["href"]
            with open(f'{dir_path}', "rb") as f:
                requests.put(href, files={"file": f})
                complete = f"\nDownload file {dir_name} is complete"
        shutil.rmtree(my_path)
        return print(complete)


vk1 = VkSaver()
vk1.get_albums()
vk1.get_photo(None, int(input("Введите id альбома: ")))
vk1.save_photo(int(input("Введите количество файлов для скачивания: ")))
ya1 = YaUploader()
ya1.upload()
