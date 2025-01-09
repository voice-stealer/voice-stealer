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
    replicas = 1

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
          image             = "cr.yandex/crpaemusgnfa4grmr44a:worker"
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

          env {
            name = "DB_HOST"
            value = yandex_mdb_postgresql_cluster.voice-stealer-pg.host[0].fqdn
          }
          env {
            name = "DB_PORT"
            value = var.database.port
          }
          env {
            name = "DB_NAME"
            value = yandex_mdb_postgresql_database.preprod-db.name
          }
          env {
            name = "DB_USER"
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
            name = "AWS_ACCESS_KEY_ID"
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
            name = "KAFKA_PORT"
            value = var.kafka_port
          }

        }
      }
    }
  }
}
