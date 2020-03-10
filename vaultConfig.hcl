storage "file" {
  path = "/Users/sam/Deployments/HashiCorp/vault_data"
}

listener "tcp" {
 address     = "127.0.0.1:8200"
 tls_disable = 1
}

ui = true

disable_mlock = true