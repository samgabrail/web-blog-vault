__author__ = 'SamG'

import pymongo, os, requests
from environs import Env

class Database(object):
    env = Env()
    # Read .env into os.environ
    env.read_env()
    SERVER = env('DB_SERVER')
    PORT = env('DB_PORT')
    # Uncomment USER and PASSWORD below to grab creds from .env file
    #USER = env('DB_USER')
    #PASSWORD = env('DB_PASSWORD')
    # Uncomment USER and PASSWORD below to show Vault's functionality
    USER = None
    PASSWORD = None
    URI = ''
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

    @staticmethod
    def initialize():
        # Uncomment the line below to show Vault's functionality
        Database.buildURI()
        Database.URI = f'mongodb://{Database.USER}:{Database.PASSWORD}@{Database.SERVER}:{Database.PORT}'
        print(f'Server: {Database.SERVER} and PORT: {Database.PORT} and user: {Database.USER} and password: {Database.PASSWORD}')
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
        try:
            return Database.DATABASE[collection].find_one(query)
        except pymongo.errors.OperationFailure:
            print(f'mongoDB auth failed due to creds expiring. Rotating creds now')
            Database.initialize()
            return Database.DATABASE[collection].find_one(query)

        