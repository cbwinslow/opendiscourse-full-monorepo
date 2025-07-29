terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.35"
    }
  }
}

provider "hcloud" {
  token = var.hcloud_token
}

data "hcloud_ssh_key" "default" {
  name = var.ssh_key_name
}

resource "hcloud_server" "default" {
  name        = var.server_name
  server_type = var.server_type
  image       = "docker-ce"
  location    = var.server_location
  ssh_keys    = [data.hcloud_ssh_key.default.id]
}

output "server_ip" {
  value = hcloud_server.default.ipv4_address
}
