resource "kubernetes_deployment" "voice-stealer-k8s-unified-agent-deployment" {
  depends_on = [
    yandex_kubernetes_cluster.voice-stealer,
    yandex_kubernetes_node_group.voice-stealer-k8s-node-group,
    kubernetes_secret.unified-agent-config,
  ]

  metadata {
    name      = "unified-agent"
    namespace = kubernetes_namespace.preprod-namespace.id
    labels = {
      name = "unified-agent"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        name = "unified-agent"
      }
    }

    template {
      metadata {
        name      = "unified-agent"
        namespace = kubernetes_namespace.preprod-namespace.id

        labels = {
          name = "unified-agent"
        }
      }

      spec {
        container {
          name              = "unified-agent"
          image             = "cr.yandex/yc/unified-agent"
          image_pull_policy = "Always"

          port {
            container_port = 16241
          }

          env {
            name  = "FOLDER_ID"
            value = var.folder_id
          }

          volume_mount {
            mount_path = "/etc/yandex/unified_agent/conf.d"
            name       = "conf"
            read_only  = true
          }

          volume_mount {
            mount_path = "/etc/jwt"
            name       = "jwt"
            read_only = true
          }
        }

        volume {
          name = "conf"
          secret {
            secret_name = kubernetes_secret.unified-agent-config.metadata[0].name
            items {
              key  = "config"
              path = "config.yml"
            }
          }
        }

        volume {
          name = "jwt"
          secret {
            secret_name = "k8s-sa-jwt"
            items {
              key = "jwt-params"
              path = "jwt_params.json"
            }
          }
        }

      }
    }
  }
}
