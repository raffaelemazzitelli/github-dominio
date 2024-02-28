variable "host" {
    type = string
}

variable "token" {
    type = string
}

variable "cluster_ca_certificate" {
    type = string
}

data "external" "test" {
  program = ["sh", "${path.module}/get_pods.sh"]

  query = {
    host                   = var.host
    token                  = var.token
    cluster_ca_certificate = var.cluster_ca_certificate
  }
}

output "test" {
  value = data.external.test
  sensitive = false
}
