__author__ = 'SamG'

import pymongo, os, requests
from environs import Env

class Database(object):
    env = Env()
    # Read .env into os.environ
    env.read_env()
    SERVER = env('DB_SERVER')
    PORT = env('DB_PORT')
    URI = ''
    USER = None
    PASSWORD = None
    DATABASE = None
    #URI = "mongodb://127.0.0.1:27017"
    # URI = f"mongodb://{SERVER}:{PORT}"

    @staticmethod
    def buildURI():
        response = requests.get(
        'http://127.0.0.1:8200/v1/database/creds/my-role',
        params={'q': 'requests+language:python'},
        headers={'X-Vault-Token': 's.GVw3pcKV1bsoqZiDCuxwMZvo'},
        )
        json_response = response.json()
        Database.USER = json_response['data']['username']
        Database.PASSWORD = json_response['data']['password']
        Database.URI = f'mongodb://{Database.USER}:{Database.PASSWORD}@{Database.SERVER}:{Database.PORT}'

    @staticmethod
    def initialize():
        Database.buildURI()
        print(f'Server: {Database.SERVER} and PORT: {Database.PORT} and URI: {Database.URI} and user: {Database.USER} and password: {Database.PASSWORD}')
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['fullstack']

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)