resource "yandex_dns_zone" "voice-stealer" {
  name = "voicestealer"

  folder_id = var.folder_id
  zone      = "voicestealer.ru."
  public    = true
}

resource "yandex_dns_recordset" "voice-stealer-www" {
  zone_id = yandex_dns_zone.voice-stealer.id
  name    = "www"
  type    = "CNAME"
  ttl     = 60
  data    = ["voicestealer.ru"]
}

resource "yandex_dns_recordset" "voice-stealer-A" {
  zone_id = yandex_dns_zone.voice-stealer.id
  name    = "@"
  type    = "A"
  ttl     = 60
  data    = [kubernetes_service.voice-stealer-k8s-api-load-balancer.status[0].load_balancer[0].ingress[0].ip]
}
