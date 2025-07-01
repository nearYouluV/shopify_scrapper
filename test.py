import requests

cookies = {
    '__RequestVerificationToken': '2PeepECnlPkgkwtsHEdACjrvT_nvW3RNlM_9inAmT9WOjBf0JjfAroXWl5ciDDVuI_WY3brhHlB1KgJNuB6V_jAl_GOq_vp3enx_wQnmFaU1',
    'ARRAffinity': '04b2e23daad7b335226461beb98df5e96b43a7b5e4952d7261c63364419b3f33',
    'ARRAffinitySameSite': '04b2e23daad7b335226461beb98df5e96b43a7b5e4952d7261c63364419b3f33',
}

headers = {
    'accept': '*/*',
    'accept-language': 'ru,en-US;q=0.9,en;q=0.8',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://directory.ausactive.org.au',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    # 'cookie': '__RequestVerificationToken=2PeepECnlPkgkwtsHEdACjrvT_nvW3RNlM_9inAmT9WOjBf0JjfAroXWl5ciDDVuI_WY3brhHlB1KgJNuB6V_jAl_GOq_vp3enx_wQnmFaU1; ARRAffinity=04b2e23daad7b335226461beb98df5e96b43a7b5e4952d7261c63364419b3f33; ARRAffinitySameSite=04b2e23daad7b335226461beb98df5e96b43a7b5e4952d7261c63364419b3f33',
}

data = {
    '__RequestVerificationToken': 'GmcB_92GljDGYJx97RRJb42yffqr3QS3goo_FuJcrLOZ0QuSfy560vX9AgC7qAS9CZ8f1QjAmzsgIUMgghLIZfihvHiEsCJr0iF_mVRuPO81',
    'PageIndex': '1',
    'Term': '',
    'PageLimit': '50',
    'OrderBy': 'none',
    'X-Requested-With': 'XMLHttpRequest',
}

response = requests.post('https://directory.ausactive.org.au/api/Search/Business', cookies=cookies, headers=headers, data=data)
import json
with open('test.json', 'w', encoding='utf-8') as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=4)