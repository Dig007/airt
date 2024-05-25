import requests
import json
import os

def refresh_access_token(refresh_token, api_key):
    refresh_url = "https://securetoken.googleapis.com/v1/token"
    headers = {
        "Content-Type": "application/json",
        "X-Android-Package": "co.appnation.artgenerator",
        "X-Android-Cert": "25F95C659B2DCEB6D38E59D2B1B7D86F9A69ED37",
        "Accept-Language": "in-ID, en-US",
        "X-Client-Version": "Android/Fallback/X22001000/FirebaseCore-Android",
        "X-Firebase-GMPID": "1:238482661076:android:11aba563876e0276246541",
        "X-Firebase-Client": "H4sIAAAAAAAAAKtWykhNLCpJSk0sKVayio7VUSpLLSrOzM9TslIyUqoFAFyivEQfAAAA",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; Redmi Note 5 Build/RQ3A.211001.001)",
        "Accept-Encoding": "gzip"
    }
    refresh_payload = {"grantType": "refresh_token", "refreshToken": refresh_token}
    refresh_response = requests.post(f"{refresh_url}?key={api_key}", headers=headers, json=refresh_payload)
    if refresh_response.status_code == 200:
        return refresh_response.json()['access_token']
    else:
        raise Exception("Failed to refresh access token")

def get_access_token(api_key, refresh_token):
    if os.path.exists("token.txt"):
        with open("token.txt", "r") as f:
            token = f.read()
        print("Token yang tersimpan ditemukan.")
    else:
        token = refresh_access_token(refresh_token, api_key)
        with open("token.txt", "w") as f:
            f.write(token)
    
    return token

def generate_image(prompt, seed, token):
    headers = {
        "user-agent": "Dart/3.1 (dart:io)",
        "userid": "p1fuQ6E5zOXsjW6xHYz1Yx7hpUJ3",
        "accept-encoding": "gzip",
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}"
    }
    url = "https://us-central1-art-generator-e907c.cloudfunctions.net/v2app/generate_with_lora"
    payload = {
        "prompt": prompt,
        "seed": seed,
        "width": 1440,
        "height": 2560,
        "num_outputs": 1,
        "nsfw": True,
        "modelKey": "sdxl",
        "key": "realistic",
        "stylePrompt": "high quqlity, Realistic, 8k",
        "negativePrompt": "cgi, cartoon, painting, illustration, (worst quality, low quality, normal quality:2)"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request failed with status code: {response.status_code}, response: {response.text}")

def save_images(image_urls, image_dir):
    for idx, image_url in enumerate(image_urls, start=1):
        extension = image_url.split(".")[-1]
        if extension in ["png", "jpeg"]:
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)
                file_name_input = input(f"Masukkan nama file untuk menyimpan gambar #{idx} (tanpa ekstensi): ")
                file_name = f"{image_dir}/{file_name_input}.{extension}"
                with open(file_name, 'wb') as image_file:
                    image_file.write(image_response.content)
                    print(f"The image has been downloaded and saved as {file_name}")
            else:
                print(f"Failed to download the image #{idx}, status code: {image_response.status_code}")
        else:
            print(f"Invalid image URL #{idx}: does not end with .png or .jpeg")

api_key = "AIzaSyABB3fgxYajNGJv40sqkbR5ZXni72TlbOQ"
refresh_token = "AMf-vBxV_S0QuUYfUmzgADDfPLzEdVJSfLb8XZwLofIQgTUaLKWgGYtEOa0WrP-mpQXPUVNyVjGjF1HF7aMlqZBmaEMTYVqIorFMIi1wmJo4Vo_YPF1pOqWgJ-jmjgNAdIEVhm9cP5pW1PkD12xs09F-dZGnrKJXZ5pCjc_10s8vHSoAfOGN6a23_GV-i_cHSzy4iXKaZWUa"

prompt = input("Masukkan masukan Anda: ")
seed = input("Masukkan seed: ")
token = get_access_token(api_key, refresh_token)

while True:
    try:
        image_urls = generate_image(prompt, seed, token)
        break
    except Exception as e:
        if "401" in str(e):
            print("Token kadaluarsa, mencoba mendapatkan token baru...")
            token = refresh_access_token(refresh_token, api_key)
            with open("token.txt", "w") as f:
                f.write(token)
        else:
            raise e

save_images(image_urls, "/sdcard/")