variable "folder_id" {
  type    = string
  default = "b1gt1qbgn0d2dvur1fes"
}

variable "network_id" {
  type    = string
  default = "enp5moohn4as8dq9elfg"
}

variable "subnet_zone" {
  type    = string
  default = "ru-central1-a"
}

variable "subnet_id" {
  type    = string
  default = "e9bn29g6evccmuu8h1s7"
}

variable "k8s-node-group" {
  type = object({
    platform_id = optional(string, "standard-v1")
    cores = optional(number, 1)
    memory = optional(number, 4)
    size = optional(number, 1)
  })
}

variable "database_port" {
  type = string
  default = "6432"
}

variable "kafka_port" {
  type = string
  default = "9092"
}

variable "aws_key_id" {
  type = string
  default = "YCAJEFDI3ulOo8HCiAi2wPZSK"
}