#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
if sys.version_info >= (3, 0):
    import imp
    imp.reload(sys)
else:
    reload(sys)
    sys.setdefaultencoding('utf8')
sys.dont_write_bytecode = True

import time
from datetime import datetime
import pytz
from logging import getLogger, StreamHandler, Formatter, FileHandler, DEBUG, INFO
import json
from pixivpy3 import *
import argparse

import AuthData

# Arg parser.
parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('--savedir', default='./downloads', type=str,
    help='The directory to save the images.')
parser.add_argument('-n', '--nIllust', default=0, type=int,
    help='The number of illustrations to get. 0 means to get all illustrations. (Caution: it does not specify the exact number.)')
parser.add_argument('--logdir', default='./logs', type=str,
    help='The directory to output the log file.')
parser.add_argument('--logLevel', default='INFO', type=str,
    help='Logging level (INFO, DEBUG)')
parser.add_argument('--enableMongoDB', action='store_true',
    help='Enable to store the metadata of images to MongoDB.')
args = parser.parse_args()

# Source: https://medium.com/lsc-psd/python%E3%81%AE%E3%83%AD%E3%82%B0%E5%87%BA%E5%8A%9B%E3%83%81%E3%83%BC%E3%83%88%E3%82%B7%E3%83%BC%E3%83%88-%E3%81%99%E3%81%90%E3%81%AB%E4%BD%BF%E3%81%88%E3%82%8B%E3%82%BD%E3%83%BC%E3%82%B9%E3%82%B3%E3%83%BC%E3%83%89%E4%BB%98-4f2ed1449674
def setup_logger(log_filename, log_level, modname=__name__):
    logger = getLogger(modname)
    if log_level == 'DEBUG':
        logger.setLevel(DEBUG)
    elif log_level == 'INFO':
        logger.setLevel(INFO)
    else:
        raise Exception('Invalid logging level!')

    sh = StreamHandler()
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    fh = FileHandler(log_filename)
    fh_formatter = Formatter('%(asctime)s - %(filename)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)
    return logger

# ISO8601-like str -> datetime
# In this api, the string format differs from ISO.
#   1. This api does not return millisecond
#   2. The UTC Offset representation differs from that of ISO.
# ref: https://qiita.com/estaro/items/2b7074839d2a5e883dc1
def convert_to_jstdt(date_str):
    date_str = date_str.split('+')[0]
    dt = None
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        dt = pytz.utc.localize(dt).astimezone(pytz.timezone("Asia/Tokyo"))
    except ValueError:
        pass
    return dt

# Escape bad string for filename (Windows)
def escape_filename(filename_str):
    import re
    bad_string = r'[\\/:*?"<>|]+'
    return re.sub(bad_string, '', filename_str)

# Define the processing for illusts (metadata)
def processItems(aapi, illusts, logger, mongoDB=None):
    processedJson = downloadImgs(aapi, illusts, logger)
    if args.enableMongoDB:
        assert mongoDB is not None
        mongoDB.insert_many(processedJson)

# Download the large images.
def downloadImgs(aapi, illusts, logger):
    # Parse datetime string in json from API for filename format.
    def _formatDateStr(convert_str):
        dt = convert_to_jstdt(convert_str)
        return dt.strftime('%Y%m%d')
    # Prefix: YYYYMMDD_MemberID_ImageID
    def _getPrefix(illust):
        create_date = _formatDateStr(illust['create_date'])
        memberId = illust['user']['id']
        imageId = illust['id']
        prefix = '{}_{}_{}'.format(create_date, memberId, imageId)
        return prefix

    # Check if the savedir exists.
    if not os.path.exists(args.savedir):
        os.makedirs(args.savedir)
    
    # Process each illust.
    for ir, illust in enumerate(illusts):
        prefix_filename = _getPrefix(illust)
        title = illust['title']
        if title == '':
            logger.info('Deleted or closed (Id:{})'.format(illust['id']))
            del illusts[ir]
            continue
        if illust['page_count'] > 1:
            # Process each images in a illust
            for ir, meta_page in enumerate(illust['meta_pages']):
                url = meta_page['image_urls']['original']
                ext = os.path.splitext(url)[-1]
                prefix_ex = 'p{}'.format(ir)
                filename = escape_filename('{}_{}_{}{}'.format(prefix_filename, prefix_ex, title, ext))
                meta_page['image_local_path'] = filename
                logger.debug(filename)
                aapi.download(url, path=args.savedir, name=filename)
                time.sleep(0.3)
        else:
            # Process single image.
            url = illust['meta_single_page']['original_image_url']
            ext = os.path.splitext(url)[-1]
            filename = escape_filename('{}_{}{}'.format(prefix_filename, title, ext))
            illust['meta_single_page']['image_local_path'] = filename
            logger.debug(filename)
            aapi.download(url, path=args.savedir, name=filename)
            time.sleep(1)
    
    return illusts

def main():
    # Init logger.
    dt = datetime.now()
    log_folder = args.logdir if args.logdir[-1] == '/' else args.logdir + '/'
    log_file = '{}{}.log'.format(log_folder, dt.strftime('%Y%m%d_%H%M'))
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    logger = setup_logger(log_file, args.logLevel)

    # Init MongoDB
    if args.enableMongoDB:
        import utils.MongoWrapper as MongoWrapper
        import MongoData
        logger.info('MongoDB initialization')
        logger.info('[Mongo Connection] Host:{}, Port:{}, DB:{}, Collection:{}'.format(MongoData.HOST, MongoData.PORT, MongoData.DBNAME, MongoData.COLLECTIONNAME))
        mongoDB = MongoWrapper.MongoWrapper(MongoData.HOST, MongoData.PORT, MongoData.DBNAME, MongoData.COLLECTIONNAME)
    else:
        mongoDB = None

    # Init AppPixivAPI.
    logger.info('PixivApi initializing...')
    api = AppPixivAPI()
    logger.info('PixivApi auth starting...')
    api.login(AuthData.USERNAME, AuthData.PASSWORD)

    # Get the images from my bookmark.
    nIllust = args.nIllust
    logger.info('PixivApi starts getting bookmarked illusts. (target id = {})'.format(AuthData.MYUSERID))
    jsonFromApi = api.user_bookmarks_illust(AuthData.MYUSERID,)
    count = len(jsonFromApi['illusts'])
    processItems(api, jsonFromApi.illusts, logger, mongoDB)
    if nIllust != 0 and count >= nIllust:
        while jsonFromApi.next_url is not None:
            next_qs = api.parse_qs(jsonFromApi.next_url)
            jsonFromApi = api.user_bookmarks_illust(**next_qs)
            count += len(jsonFromApi.illusts)
            processItems(api, jsonFromApi.illusts, logger, mongoDB)
            if nIllust != 0 and count >= nIllust:
                logger.info('Processed:{} of {}. Break.'.format(count, args.nIllust))
                break
    logger.info('Finished processing all items. Number of item: {}'.format(count))

if __name__ == '__main__':
    main()