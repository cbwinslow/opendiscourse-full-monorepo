variable "oci_region" { type = string }
variable "tenancy_ocid" { type = string }
variable "user_ocid" { type = string }
variable "api_fingerprint" { type = string }
variable "api_private_key_path" { type = string }
variable "compartment_ocid" { type = string }
variable "subnet_ocid" { type = string }
variable "ssh_public_key" { type = string }
variable "db_display_name" { type = string }
variable "db_hostname" { type = string }

variable "cloudflare_account_id" { type = string }
variable "cloudflare_api_token" { type = string }
variable "tunnel_name" { type = string }
variable "tunnel_secret" { type = string }
variable "r2_bucket_name" { type = string }
