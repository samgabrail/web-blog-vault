Web blog
========

This is a simple web blog to demo use cases with Hashicorp Vault. The app communicates directly with Vault using the API.

It uses python, flask, bootstrap, mongodb, consul, and vault.

# [MongoDB Setup](https://docs.mongodb.com/manual/tutorial/enable-authentication/)

## Create admin user creds
From the mongo client inside the __admin__ database run the following:
```shell
db.createUser(
  {
    user: "sam",
    pwd: "test123", // or cleartext password
    roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]
  }
)
```
Exit the mongo client
## Start the mongod instance with authentication enabled
```shell
sudo mongod --auth --port 27017 --dbpath /Users/sam/Deployments/HashiCorp/mongo_data
```

## Start a new terminal window and authenticate as an admin user
```shell
mongo --port 27017  --authenticationDatabase "admin" -u "sam" -p "test123"
```

# [Vault setup](https://www.vaultproject.io/docs/secrets/databases/mongodb.html)

## Using File Storage Backend
Start the vault server using a config file. 
```shell
vault server -config=vaultConfig.hcl
```
Content of the config file are below:
```shell
storage "file" {
  path = "/Users/sam/Deployments/HashiCorp/vault_data"
}

listener "tcp" {
 address     = "127.0.0.1:8200"
 tls_disable = 1
}

disable_mlock = true
```
## Initializing the Vault

```shell
export VAULT_ADDR='http://127.0.0.1:8200'
vault operator init -key-shares=1 -key-threshold=1
```
You get the following output. In production you typically would use [Vault's PGP and Keybase.io](https://www.vaultproject.io/docs/concepts/pgp-gpg-keybase.html) support to encrypt each of these keys so only one person has access to one key only.
```
Unseal Key 1: 258G83eRO8SMqFWBRs9Bn+8yAdK7HVgtMiAkgOdh5iA=

Initial Root Token: s.ewt0JUqVxTVnU7fW04ZiKiYh

```

## Unseal the Vault
Run the following command to unseal
```shell
vault operator unseal
```

## Authenticate with the initial root token
```shell
vault login s.ewt0JUqVxTVnU7fW04ZiKiYh
```

## Enable the database secrets engine
```shell
vault secrets enable database
```

## Configure Vault with the mongoDB plugin
```shell
vault write database/config/my-mongodb-database \
    plugin_name=mongodb-database-plugin \
    allowed_roles="my-role" \
    connection_url="mongodb://{{username}}:{{password}}@127.0.0.1:27017/admin" \
    username="sam" \
    password="test123"
```

## Configure a role that maps a name in Vault to a MongoDB command that executes and creates the database credential
```shell
vault write database/roles/my-role \
    db_name=my-mongodb-database \
    creation_statements='{ "db": "admin", "roles": [{ "role": "readWriteAnyDatabase" }, {"role": "read", "db": "foo"}] }' \
    default_ttl="10s" \
    max_ttl="24h"
```

## Manually Test
```shell
vault read database/creds/my-role
```

## [Use the Vault API](https://www.vaultproject.io/api/secret/databases/index.html#generate-credentials)
### Sample Request
Change the `X-Vault-Token` value below to work for yours.
```shell
$ curl \
    --header "X-Vault-Token: s.ewt0JUqVxTVnU7fW04ZiKiYh" \
    http://127.0.0.1:8200/v1/database/creds/my-role
```

### Sample Response
```json
{
  "data": {
    "username": "root-1430158508-126",
    "password": "132ae3ef-5a64-7499-351e-bfe59f3a2a21"
  }
}
```

### Python Example
Change the `X-Vault-Token` value below to yours.
```python
response = requests.get(
'http://127.0.0.1:8200/v1/database/creds/my-role',
params={'q': 'requests+language:python'},
headers={'X-Vault-Token': 's.ewt0JUqVxTVnU7fW04ZiKiYh'},
)
json_response = response.json()
Database.USER = json_response['data']['username']
Database.PASSWORD = json_response['data']['password']
Database.URI = f'mongodb://{Database.USER}:{Database.PASSWORD}@{Database.SERVER}:{Database.PORT}'
```

# Demo Steps

0. Make sure you're logged out of the app. Have the VS code screen with the teriminal output showing. Also have the VS code screen side by side to the Chrome screen. My email is **sam** and password is **test123** to access the app.
1. Comment and uncomment the lines in `databse.py` and `.env` to show the static hard-coded creds scenario.
2. Log into the app
3. Show the stdout in VS code's terminal showing the hard-coded username and password are the same as those in the `.env` file.
4. Browse the Blogs page to show that the creds don't expire.
5. Log out of the app
6. Comment and uncomment the lines in `databse.py` and `.env` to show the dynamic secrets scenario using Vault
7. Log into the app
8. Show the stdout in VS code's terminal showing the auto-generated username and password by vault.
9. Browse the Blogs page to show that the creds expire and we get a message saying `mongoDB auth failed due to creds expiring. Rotating creds now`. Then we get new creds.
10. Pivot over to a terminal with the mongo client running. Make sure you're logged in as an admin. Run the commands: `use admin` and `show users`. Show how the creds appear and disappear based on the timeout. You will need to browse the web blog to generate new creds.