#!/usr/bin/env python3
# My utility for using MongoDB.

from pymongo import MongoClient

class MongoWrapper:
    def __init__(self, host, port, dbName, collectionName):
        self.host = host
        self.port = port
        self.client = MongoClient(host, port)
        self.db = self.client[dbName]
        self.collection = self.db[collectionName]

    def insert_one(self, document):
        return self.collection.insert_one(document)

    def insert_many(self, documents):
        return self.collection.insert_many(documents)