# PixivImageTool
## Overview
This is a tool for downloading images from Pixiv using [PyPixiv](https://github.com/Yukariin/PyPixiv).

## Prerequisites
- Install dependency.

```bash
pip install -r requirements.txt
```

- Add `AuthData.py` to the root directory. This stores your auth data in order to login.
    - *As of Mar. 19th 2021, login with username/password cannot be used, use refresh_token*
    - Please refer to [Pixivpy3 repository](https://github.com/upbit/pixivpy) about how to get refresh_token.
        - I have implemented auto-login functionality on [this code](https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362#file-pixiv_auth-py). Thanks to his great work!
            - I won't answer to this function's usage. And please use at your own risk.
```AuthData.py
USERNAME = 'user'               # Your username (Currently unsupported)
PASSWORD = 'password'           # Your password (Currently unsupported)
REFRESH_TOKEN = 'refresh_token' # Refresh token
MYUSERID = <id>                 # Your id
```
- (Optional) Add `MongoData.py` to the root directory if you would like to use MongoDB for saving metadata.

```MongoData.py
HOST = '127.0.0.1'
PORT = <Port>
DBNAME = 'PixivMetaData'
COLLECTIONNAME = 'MyFavIllusts'
```

## Usage

- To just download all your favorite illustrations, you just run:

```
python download_bookmark_illust.py
```

- For further, run:

```
python download_bookmark_illust.py -h
```

## License
[CC0](https://creativecommons.org/share-your-work/public-domain/cc0)