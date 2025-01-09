resource "yandex_iam_service_account" "k8s-deploy-sa" {
  name      = "k8s-deploy-sa"
  folder_id = var.folder_id
}

resource "yandex_resourcemanager_folder_iam_member" "k8s-deploy-sa-editor" {
  folder_id = var.folder_id
  role      = "editor"
  member    = "serviceAccount:${yandex_iam_service_account.k8s-deploy-sa.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "k8s-deploy-sa-images-puller" {
  folder_id = var.folder_id
  role      = "container-registry.images.puller"
  member    = "serviceAccount:${yandex_iam_service_account.k8s-deploy-sa.id}"
}
