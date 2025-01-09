resource "helm_release" "strimzi_kafka_operator" {
  name       = "strimzi-kafka-operator"
  namespace  = "kafka-namespace"
  repository = "https://strimzi.io/charts/"
  chart      = "strimzi-kafka-operator"
  version    = "0.37.0"

  create_namespace = true

  set {
    name  = "watchAnyNamespace"
    value = true
  }
}

resource "kubernetes_namespace" "kafka" {
  metadata {
    name = "kafka-namespace"
  }
}

resource "kubernetes_manifest" "kafka_nodepool" {
  manifest = {
    "apiVersion" = "kafka.strimzi.io/v1beta2"
    "kind"       = "KafkaNodePool"
    "metadata" = {
      "name"      = "dual-role"
      "namespace" = "preprod"
      "labels" = {
        "strimzi.io/cluster" = "my-cluster"
      }
    }
    "spec" = {
      "replicas" = 1
      "roles" = ["controller", "broker"]
      "storage" = {
        "type" = "jbod"
        "volumes" = [
          {
            "id"            = 0
            "type"          = "persistent-claim"
            "size"          = "5Gi"
            "deleteClaim"   = false
            "kraftMetadata" = "shared"
          }
        ]
      }
    }
  }
}

resource "kubernetes_manifest" "kafka_cluster" {
  manifest = {
    "apiVersion" = "kafka.strimzi.io/v1beta2"
    "kind"       = "Kafka"
    "metadata" = {
      "name"      = "my-cluster"
      "namespace" = "preprod"
      "labels" = {
        "name" = "kafka"
      }
      "annotations" = {
        "strimzi.io/node-pools" = "enabled"
        "strimzi.io/kraft"      = "enabled"
      }
    }
    "spec" = {
      "kafka" = {
        "version"  = "3.5.1"
        "replicas" = 1
        "listeners" = [
          {
            "name" = "plain"
            "port" = 9092
            "type" = "internal"
            "tls"  = false
          },
          {
            "name" = "tls"
            "port" = 9093
            "type" = "internal"
            "tls"  = false
          }
        ]

        "storage" = {
          "type" = "jbod"
          "volumes" = [
            {
              "id"          = 0
              "type"        = "persistent-claim"
              "size"        = "5Gi"
              "deleteClaim" = false
            }
          ]
        }

        "config" = {
          "offsets.topic.replication.factor"         = 1
          "transaction.state.log.replication.factor" = 1
          "transaction.state.log.min.isr"            = 1
          "default.replication.factor"               = 1
          "min.insync.replicas"                      = 1
        }
      }

      "zookeeper" = {
        "replicas" = 1
        "storage" = {
          "type"        = "persistent-claim"
          "size"        = "10Gi"
          "deleteClaim" = false
        }
      }

      "entityOperator" = {
        "topicOperator" = {}
        "userOperator" = {}
      }
    }
  }
}

resource "kubernetes_manifest" "kafka_input_topic" {
  manifest = {
    "apiVersion" = "kafka.strimzi.io/v1beta2"
    "kind"       = "KafkaTopic"
    "metadata" = {
      "name"      = "requests"
      "namespace" = "preprod"
      "labels" = {
        "strimzi.io/cluster" = "my-cluster"
      }
    }
    "spec" = {
      "partitions" = 1
      "replicas"   = 1
    }
  }
}

resource "kubernetes_manifest" "kafka_logs_topic" {
  manifest = {
    "apiVersion" = "kafka.strimzi.io/v1beta2"
    "kind"       = "KafkaTopic"
    "metadata" = {
      "name"      = "logs"
      "namespace" = "preprod"
      "labels" = {
        "strimzi.io/cluster" = "my-cluster"
      }
    }
    "spec" = {
      "partitions" = 1
      "replicas"   = 1
    }
  }
}

data "kubernetes_service" "kafka_bootstrap" {
  metadata {
    name      = "my-cluster-kafka-bootstrap"
    namespace = "preprod"
  }
}
