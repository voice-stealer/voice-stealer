resource "yandex_logging_group" "voice-stealer-k8s-audit-logs" {
  name        = "voice-stealer-k8s-audit-logs"
  description = "Kubernetes audit logs"
  folder_id   = var.folder_id

  retention_period      = "72h"
}