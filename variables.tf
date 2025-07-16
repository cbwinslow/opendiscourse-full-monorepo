variable "hcloud_token" {
  description = "Hetzner Cloud API token"
  type        = string
  sensitive   = true
}

variable "server_name" {
  description = "Name of the server"
  type        = string
  default     = "opendiscourse-server"
}

variable "server_type" {
  description = "Type of the server"
  type        = string
  default     = "cx11"
}

variable "server_location" {
  description = "Location of the server"
  type        = string
  default     = "nbg1"
}

variable "ssh_key_name" {
  description = "Name of the SSH key to use"
  type        = string
}
