resource "kubernetes_deployment" "voice-stealer-k8s-worker-deployment" {
  depends_on = [
    yandex_kubernetes_cluster.voice-stealer,
    yandex_kubernetes_node_group.voice-stealer-k8s-node-group,
  ]

  metadata {
    name      = "worker"
    namespace = kubernetes_namespace.preprod-namespace.id
    labels = {
      name = "worker"
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        name = "worker"
      }
    }

    template {
      metadata {
        name      = "worker"
        namespace = kubernetes_namespace.preprod-namespace.id

        labels = {
          name = "worker"
        }
      }

      spec {
        container {
          name              = "worker"
          image             = "cr.yandex/crpaemusgnfa4grmr44a:worker-20250110-1223"
          image_pull_policy = "Always"

          command = [
            "python",
            "main.py"
          ]

          resources {
            requests = {
              memory = "1Gi"
            }
          }

          port {
            container_port = 2112
          }

          env {
            name  = "DB_HOST"
            value = yandex_mdb_postgresql_cluster.voice-stealer-pg.host[0].fqdn
          }
          env {
            name  = "DB_PORT"
            value = var.database_port
          }
          env {
            name  = "DB_NAME"
            value = yandex_mdb_postgresql_database.preprod-db.name
          }
          env {
            name  = "DB_USER"
            value = yandex_mdb_postgresql_user.voice-stealer-preprod.name
          }
          env {
            name = "DB_PASSWORD"
            value_from {
              secret_key_ref {
                name = "db-password"
                key  = "password"
              }
            }
          }

          env {
            name  = "AWS_ACCESS_KEY_ID"
            value = var.aws_key_id
          }
          env {
            name = "AWS_SECRET_ACCESS_KEY"
            value_from {
              secret_key_ref {
                name = "aws-secret-access-key"
                key  = "key"
              }
            }
          }

          env {
            name  = "KAFKA_HOST"
            value = data.kubernetes_service.kafka_bootstrap.spec[0].cluster_ip
          }
          env {
            name  = "KAFKA_PORT"
            value = var.kafka_port
          }

        }
      }
    }
  }
}

data "external" "get_worker_pod_ips" {
  program = [
    "bash", "-c", <<EOF
    kubectl -n preprod get pods -l name=worker -o jsonpath='{.items[*].status.podIP}' | jq -R '{ips: .}'
    EOF
  ]
}

locals {
  worker_pod_ips = split(" ", data.external.get_worker_pod_ips.result["ips"])
}

output "worker_pod_ips_list" {
  value = local.worker_pod_ips
}
