resource "yandex_kubernetes_cluster" "voice-stealer" {
  name = "voice-stealer"

  network_id = var.network_id
  folder_id  = var.folder_id
  master {
    public_ip = true
    master_location {
      zone      = var.subnet_zone
      subnet_id = var.subnet_id
    }
    master_logging {
      enabled                    = true
      log_group_id               = yandex_logging_group.voice-stealer-k8s-audit-logs.id
      kube_apiserver_enabled     = true
      cluster_autoscaler_enabled = true
      events_enabled             = true
      audit_enabled              = true
    }
  }
  service_account_id      = yandex_iam_service_account.k8s-deploy-sa.id
  node_service_account_id = yandex_iam_service_account.k8s-deploy-sa.id
  depends_on = [
    yandex_resourcemanager_folder_iam_member.k8s-deploy-sa-editor,
    yandex_resourcemanager_folder_iam_member.k8s-deploy-sa-images-puller,
    yandex_logging_group.voice-stealer-k8s-audit-logs,
  ]
}

resource "yandex_kubernetes_node_group" "voice-stealer-k8s-node-group" {
  cluster_id = yandex_kubernetes_cluster.voice-stealer.id
  name       = "voice-stealer-k8s-node-group"

  allocation_policy {
    location {
      zone = var.subnet_zone
    }
  }

  instance_template {
    platform_id = var.k8s-node-group.platform_id

    network_interface {
      ipv4 = true
      subnet_ids = [var.subnet_id]
      nat  = true
    }
    resources {
      cores  = var.k8s-node-group.cores
      memory = var.k8s-node-group.memory
    }
    boot_disk {
      size = 30
      type = "network-ssd"
    }
  }
  scale_policy {
    fixed_scale {
      size = var.k8s-node-group.size
    }
  }
}

resource "kubernetes_namespace" "preprod-namespace" {
  metadata {
    name = "preprod"
  }
}
