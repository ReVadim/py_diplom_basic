import requests
from pprint import pprint
import time

# ya_disk_api = input("input your REST API token: ")
# owner_id = input("input your id: ")

with open('token.txt', 'r') as t, open('Ya_disk_api.txt', 'r') as y:
    token = t.read().strip()
    ya_disk_api = y.read().strip()

ya_url = 'https://cloud-api.yandex.net/v1/disk/'


class VkSaver:
    def __init__(self, owner_id=None):
        self.token = token
        self.url = 'http://api.vk.com/method/'
        self.owner_id = owner_id
        self.version = '5.126'
        self.photo_stock = {}
        self.albums_list = {}
        self.params = {
            'access_token': self.token,
            'v': self.version,
        }
        if owner_id is None:
            self.owner_id = requests.get(self.url+'users.get', self.params).json()['response'][0]['id']

    def get_albums(self, owner_id=None):
        """find all owner photo albums"""
        if id is None:
            owner_id = self.owner_id
        album_url = self.url + 'photos.getAlbums'
        album_params = {
            'user_id': owner_id,
        }
        response = requests.get(album_url, params={**self.params, **album_params}).json()['response']
        time.sleep(0.4)
        count_albums = response['count']
        print("Количество альбомов = ", count_albums)
        for items in response['items']:
            self.albums_list[str(items['id'])] = items['title']
        print(self.albums_list)

    def get_photo(self, user_id=None, album_id=None):
        if user_id is None:
            user_id = self.owner_id
        if album_id is None:
            album_id = 'profile'
        gp_params = {
            'user_id': user_id,
            'extended': 1,
            'photo_sizes': 1,
            'album_id': album_id
        }
        response = requests.get(self.url+'photos.get', params={**self.params, **gp_params}).json()['response']
        time.sleep(0.4)
        count_photos = response['count']
        for items in response['items']:
            self.photo_stock[items['id']] = [items['likes']['count'], items['sizes'][-1]['url']]
            time.sleep(0.4)

        print(f"В альбоме {count_photos} фото")
        print(self.photo_stock)

    def get_max_photos(self):
        pass

    def make_dir(self):
        """make dir"""
        dir_name = 'test_dir'  # need to create
        make_dir_url = ya_url + 'resources'
        requests.put(make_dir_url,
                     params={"path": f"{dir_name}"},
                     headers={"Authorization": f"OAuth {Ya_disk_api}"}
                     )


class YaUploader:
    def __init__(self, api_token: str):
        self.headers = {"Authorization": f"OAuth {ya_disk_api}"}

    def upload(self, file_path: str):
        """Метод загруджает файлы из папки на яндекс диск"""
        my_dir = file_path.split('\\')
        dir_name = my_dir[-1]
        contents = []
        for item in os.walk(dir_path):
            contents.append(item)
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
                            params={"path": f"{dir_name}/{elem+'copy'}"},
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
        return print(complete)


vk1 = VkSaver()
vk1.get_albums()
# vk1.get_photo(None, 168628450)
vk1.get_photo(None, int(input("Введите id альбома: ")))
#
#
#
#
# """progress"""
# part = int(count / part_way)
# status = round(count * percent + ost)
# print(f"[{count} / {len(files)}] {'##' * part + '--' * (10 - part)} {status} % || {elem}\r")
# time.sleep(.1)
# count += 1