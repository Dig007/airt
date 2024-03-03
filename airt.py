import requests
import json
import os

# Fungsi untuk merefresh access token
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
    refresh_payload = {
        "grantType": "refresh_token",
        "refreshToken": refresh_token
    }

    refresh_response = requests.post(f"{refresh_url}?key={api_key}", headers=headers, json=refresh_payload)
    if refresh_response.status_code == 200:
        return refresh_response.json()['access_token']
    else:
        raise Exception("Failed to refresh access token")

# Fungsi untuk membuat request POST
def make_post_request(url, headers, payload, refresh_token, api_key):
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 401:  # Unauthorized, token mungkin kedaluwarsa
        token = get_access_token()  # Dapatkan token baru
        headers['authorization'] = f"Bearer {token}"  # Perbarui token
        response = requests.post(url, headers=headers, json=payload)  # Coba request lagi dengan token baru
    return response

# Fungsi untuk mendapatkan token dari file
def get_access_token():
    # Periksa apakah file token.txt ada
    if os.path.exists("token.txt"):
        # Baca file token.txt
        with open("token.txt", "r") as f:
            token = f.read()
        print("Token yang tersimpan ditemukan.")
        return token
    else:
        # Jika file tidak ada, dapatkan token baru
        api_key = "AIzaSyABB3fgxYajNGJv40sqkbR5ZXni72TlbOQ"
        refresh_token = "AMf-vBxV_S0QuUYfUmzgADDfPLzEdVJSfLb8XZwLofIQgTUaLKWgGYtEOa0WrP-mpQXPUVNyVjGjF1HF7aMlqZBmaEMTYVqIorFMIi1wmJo4Vo_YPF1pOqWgJ-jmjgNAdIEVhm9cP5pW1PkD12xs09F-dZGnrKJXZ5pCjc_10s8vHSoAfOGN6a23_GV-i_cHSzy4iXKaZWUa"  # Tempatkan refresh token yang valid
        token = refresh_access_token(refresh_token, api_key)
        
        # Simpan token baru ke file
        with open("token.txt", "w") as f:
            f.write(token)
        return token

api_key = "AIzaSyABB3fgxYajNGJv40sqkbR5ZXni72TlbOQ"
refresh_token = "AMf-vBxV_S0QuUYfUmzgADDfPLzEdVJSfLb8XZwLofIQgTUaLKWgGYtEOa0WrP-mpQXPUVNyVjGjF1HF7aMlqZBmaEMTYVqIorFMIi1wmJo4Vo_YPF1pOqWgJ-jmjgNAdIEVhm9cP5pW1PkD12xs09F-dZGnrKJXZ5pCjc_10s8vHSoAfOGN6a23_GV-i_cHSzy4iXKaZWUa"  # Tempatkan refresh token yang valid

# Dapatkan token dari file
token = get_access_token()

# Tentukan headers untuk request POST
headers = {
    "user-agent": "Dart/3.1 (dart:io)",
    "userid": "p1fuQ6E5zOXsjW6xHYz1Yx7hpUJ3",
    "accept-encoding": "gzip",
    "content-type": "application/json; charset=utf-8",
    "authorization": f"Bearer {token}"
}

url = "https://us-central1-art-generator-e907c.cloudfunctions.net/test/create_art_with_replicate"
masukan = input("Masukkan masukan Anda: ")
seed = input("Masukkan seed: ")

payload = {
    "version": "8beff3369e81422112d93b89ca01426147de542cd4684c244b673b105188fe5f",
    "prompt": masukan,
    "seed": seed,
    "width": 1080,
    "height": 1920,
    "num_outputs": 1,
    "nsfw": True,
    "model_key": "sdxl"
}

# Lakukan request dan tangani refresh token jika diperlukan
response = make_post_request(url, headers, payload, refresh_token, api_key)
if response.status_code == 200:
    response_json = response.json()
    
    # Print JSON response
    print(json.dumps(response_json, indent=4))  # Print JSON formatted response
    
    # Assumption: response_json adalah list dari URLs dalam format PNG
    if isinstance(response_json, list):
        for idx, image_url in enumerate(response_json, start=1):
            if image_url.endswith('.png'):
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    image_dir = "/sdcard/AI/"
                    if not os.path.exists(image_dir):
                        os.makedirs(image_dir)
                    file_name_input = input(f"Masukkan nama file untuk menyimpan gambar #{idx} (tanpa ekstensi): ")
                    file_name = f"{image_dir}{file_name_input}.png"
                    with open(file_name, 'wb') as image_file:
                        image_file.write(image_response.content)
                        print(f"The image has been downloaded and saved as {file_name}")
                else:
                    print(f"Failed to download the image #{idx}, status code: {image_response.status_code}")
            else:
                print(f"Invalid image URL #{idx}: does not end with .png")
    else:
        print("Invalid response format. Response should be a list of image URLs.")
else:
    print(f"Request failed with status code: {response.status_code}, response: {response.text}")