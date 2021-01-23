# PixivImageTool
## Overview
This is a tool for downloading images from Pixiv using [PyPixiv](https://github.com/Yukariin/PyPixiv).

## Prerequisites
- Install dependency.

```bash
pip install -r requirements.txt
```

- Add `AuthData.py` to the root directory. This stores your auth data in order to login.

```AuthData.py
USERNAME = 'user'           # Your username
PASSWORD = 'password'       # Your password
MYUSERID = <id>             # Your id
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