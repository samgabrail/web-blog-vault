Web blog
========

This is a simple web blog to demo use cases with Hashicorp Vault.

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
sudo mongod --auth --port 27017 --dbpath /var/lib/mongodb
```

## Start a new terminal window and authenticate as an admin user
```shell
mongo --port 27017  --authenticationDatabase "admin" -u "sam" -p "test123"
```

# [Consul Setup](https://learn.hashicorp.com/consul/getting-started/agent)

We used consul for our storage backend for Vault. Run the command below to start consul in dev mode and enable the UI.
```shell
consul agent -dev -ui
```

You can then access the UI at:
http://127.0.0.1:8500/ui

# [Vault setup](https://www.vaultproject.io/docs/secrets/databases/mongodb.html)

## Using Consul for HA
Start the vault server using a config file. 
```shell
vault server -config=vaultConfig.hcl
```
Content of the config file are below:
```shell
storage "consul" {
  address = "127.0.0.1:8500"
  path    = "vault/"
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
vault operator init
```
You get the following output. In production you typically would use [Vault's PGP and Keybase.io](https://www.vaultproject.io/docs/concepts/pgp-gpg-keybase.html) support to encrypt each of these keys so only one person has access to one key only.
```
Unseal Key 1: VOOYrwXlaWwDWuZCqH0gjgmx/mjYQtGRtoLxmX86Pg8d
Unseal Key 2: dmSynGa7RJSy62QNcL0kpfVN6g3TGqnFyKL1OHB87y/w
Unseal Key 3: u4FNe+qksiMVd4PwOzLJV3ESepu7RWeKBq8k5d8hDM0O
Unseal Key 4: PHtDhEQWUbgPjfKLV1ml4Mzm4WvZn5jwWP5c/D4f1DD7
Unseal Key 5: 6S5CRlIUHgyDJQaHFaVcbtzOQPnr2UAszP4vhjv1cYP2

Initial Root Token: s.GVw3pcKV1bsoqZiDCuxwMZvo

Vault initialized with 5 key shares and a key threshold of 3. Please securely
distribute the key shares printed above. When the Vault is re-sealed,
restarted, or stopped, you must supply at least 3 of these keys to unseal it
before it can start servicing requests.

Vault does not store the generated master key. Without at least 3 key to
reconstruct the master key, Vault will remain permanently sealed!

It is possible to generate new unseal keys, provided you have a quorum of
existing unseal keys shares. See "vault operator rekey" for more information.
```

## Unseal the Vault
Run the following command 3 times providing 3 out of the 5 unseal keys.
```shell
vault operator unseal
```

## Authenticate with the initial root token
```shell
vault login s.GVw3pcKV1bsoqZiDCuxwMZvo
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
```shell
$ curl \
    --header "X-Vault-Token: ..." \
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
```python
response = requests.get(
'http://127.0.0.1:8200/v1/database/creds/my-role',
params={'q': 'requests+language:python'},
headers={'X-Vault-Token': 's.2U3je9neQkO9OEutL6x8kdcz'},
)
json_response = response.json()
Database.USER = json_response['data']['username']
Database.PASSWORD = json_response['data']['password']
Database.URI = f'mongodb://{Database.USER}:{Database.PASSWORD}@{Database.SERVER}:{Database.PORT}'
```

# Demo Steps

0. Make sure you're logged out of the app. Have the VS code screen with the teriminal output showing. Also have the VS code screen side by side to the Chrome screen.
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