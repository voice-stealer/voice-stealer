resource "kubernetes_service" "voice-stealer-k8s-api-load-balancer" {
  metadata {
    name      = "api"
    namespace = "preprod"
  }

  spec {
    selector = {
      name = kubernetes_deployment.voice-stealer-k8s-api-deployment.spec[0].template[0].metadata[0].labels.name
    }

    port {
      name        = "http"
      port        = 443
      target_port = 443
    }

    type = "LoadBalancer"
  }

}

resource "kubernetes_deployment" "voice-stealer-k8s-api-deployment" {
  depends_on = [
    yandex_kubernetes_cluster.voice-stealer,
    yandex_kubernetes_node_group.voice-stealer-k8s-node-group,
  ]

  metadata {
    name      = "api"
    namespace = kubernetes_namespace.preprod-namespace.id
    labels = {
      name = "api"
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        name = "api"
      }
    }

    template {
      metadata {
        name      = "api"
        namespace = kubernetes_namespace.preprod-namespace.id

        labels = {
          name = "api"
        }
      }

      spec {
        container {
          name              = "api"
          image             = "cr.yandex/crpaemusgnfa4grmr44a:api"
          image_pull_policy = "Always"

          command = [
            "python",
            "main.py"
          ]

          resources {
            limits = {
              memory = "1Gi"
            }
          }

          env {
            name = "SECRET_KEY"
            value_from {
              secret_key_ref {
                name = "api-secret-key"
                key  = "secret-key"
              }
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

          volume_mount {
            mount_path = "/etc/api-certificate"
            name       = "api-cert"
            read_only = true
          }

          volume_mount {
            mount_path = "/etc/api-certificate-key"
            name       = "api-cert-key"
            read_only = true
          }
        }

        volume {
          name = "api-cert"
          secret {
            secret_name = "api-cert-certificate"
            items {
              key = "cert"
              path = "certificate.crt"
            }
          }
        }

        volume {
          name = "api-cert-key"
          secret {
            secret_name = "api-cert-key"
            items {
              key = "key"
              path = "certificate.key"
            }
          }
        }
      }
    }
  }
}
