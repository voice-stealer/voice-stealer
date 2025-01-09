resource "yandex_mdb_postgresql_cluster" "voice-stealer-pg" {
  name                = "voice-stealer"
  environment         = "PRODUCTION"
  folder_id           = var.folder_id
  network_id          = var.network_id
  security_group_ids = []
  deletion_protection = true

  config {
    version = 17
    resources {
      resource_preset_id = "s2.micro"
      disk_type_id       = "network-ssd"
      disk_size          = "20"
    }
  }

  host {
    zone             = "ru-central1-a"
    name             = "voice-stealer-pg-host-a"
    subnet_id        = var.subnet_id
    assign_public_ip = true
  }
}

resource "yandex_mdb_postgresql_database" "preprod-db" {
  cluster_id = yandex_mdb_postgresql_cluster.voice-stealer-pg.id
  name       = "preprod"
  owner      = "voice-stealer-preprod"
}

resource "yandex_mdb_postgresql_user" "voice-stealer-preprod" {
  cluster_id = yandex_mdb_postgresql_cluster.voice-stealer-pg.id
  name       = "voice-stealer-preprod"
  password   = "*REPLACED*"
}
