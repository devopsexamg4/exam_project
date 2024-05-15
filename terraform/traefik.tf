resource "google_compute_disk" "my_data_disk" {
  name  = "my-data-disk"
  type  = "pd-standard"
  size  = 1
  zone  = "europe-north1-a"
}

resource "kubernetes_persistent_volume" "traefik-vol" {
  metadata {
    name = "traefik-vol"
  }
  spec {
    capacity = {
      storage = "1Gi"
    }
    access_modes = ["ReadWriteOnce"]
    storage_class_name = "standard-rwo"
    persistent_volume_source {
      gce_persistent_disk {
        pd_name = google_compute_disk.my_data_disk.name
        fs_type = "ext4"
      }
    }
  }
}

resource "kubernetes_persistent_volume_claim" "traefik-vol" {
  metadata {
    name = "traefik-vol"
  }
  spec {
    access_modes = ["ReadWriteOnce"]
    storage_class_name = "standard-rwo"
    resources {
      requests = {
        storage = "1Gi"
      }
    }
    volume_name = kubernetes_persistent_volume.traefik-vol.metadata[0].name
  }
}

resource "kubernetes_deployment" "traefik_deployment" {
  metadata {
    name = "traefik-deployment"
    labels = {
      app = "traefik"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "traefik"
      }
    }

    template {
      metadata {
        labels = {
          app = "traefik"
        }
      }

      spec {
        service_account_name = "traefik-account"

        volume {
          name = "traefik-data"

          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.traefik-vol.metadata[0].name
          }
        }

        volume {
          name = "gcloud-service"

          secret {
            secret_name = "traefik-dns-acc"
          }
        }

        init_container {
          name  = "volume-permissions"
          image = "busybox:1.36.1"

          command = ["sh", "-c", "touch /letsencrypt/acme.json && chmod -Rv 600 /letsencrypt/* && chown 65532:65532 /letsencrypt/acme.json"]

          volume_mount {
            mount_path = "/letsencrypt"
            name       = "traefik-data"
          }
        }

        container {
          name  = "traefik"
          image = "traefik:v2.11"

          args = [
            "--providers.kubernetesingress",
            "--certificatesresolvers.myresolver.acme.email=andreas.askholm@gmail.com",
            "--certificatesresolvers.myresolver.acme.dnschallenge.provider=gcloud",
            "--certificatesresolvers.myresolver.acme.dnschallenge=true",
            "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json",
            "--certificatesresolvers.myresolver.acme.caServer=https://acme-staging-v02.api.letsencrypt.org/directory",
            "--entrypoints.web.http.redirections.entrypoint.to=websecure",
            "--entrypoints.web.http.redirections.entrypoint.scheme=https",
            "--entrypoints.web.address=:80",
            "--entrypoints.websecure.address=:443",
            "--entrypoints.websecure.http.tls=true",
            "--entrypoints.websecure.http.tls.certresolver=myresolver",
            "--log=true",
            "--log.format=json",
            "--log.level=WARNING"
          ]

          env {
            name  = "GCE_SERVICE_ACCOUNT_FILE"
            value = "/etc/service-account.json"
          }

          env {
            name = "GCE_PROJECT"

            value_from {
              secret_key_ref {
                key  = "project"
                name = "gcloud-project"
              }
            }
          }

          port {
            name           = "web"
            container_port = 80
          }

          port {
            name           = "websecure"
            container_port = 443
          }

          volume_mount {
            mount_path = "/letsencrypt"
            name       = "traefik-data"
          }

          volume_mount {
            mount_path = "/etc/service-account.json"
            name       = "gcloud-service"
            read_only  = true
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "traefik_web_service" {
  metadata {
    name = "traefik-web-service"
  }

  spec {
    type = "LoadBalancer"

    port {
      port        = 80
      target_port = "web"
    }

    selector = {
      app = "traefik"
    }
  }
}

resource "kubernetes_service" "traefik_websec_service" {
  metadata {
    name = "traefik-websec-service"
  }

  spec {
    type = "LoadBalancer"

    port {
      port        = 443
      target_port = "websecure"
    }

    selector = {
      app = "traefik"
    }
  }
}