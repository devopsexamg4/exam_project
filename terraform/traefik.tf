data "google_secret_manager_secret_version" "duckdns_token" {
    secret = "default_duckdns_token"
    version = "latest"
}

resource "kubernetes_deployment" "traefik_deployment" {
    metadata {
        name = "traefik-deployment"
        namespace = "NAMESPACE_NAME"
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
                service_account_name = "traefik-ingress-controller"

                volume {
                    name = "traefik-data"
                    persistent_volume_claim {
                        claim_name = "traefik-vol"
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
                    image = "traefik:v3.0"

                    resources {
                        limits = {
                            cpu    = "1"
                            memory = "1Gi"
                        }
                        requests = {
                            cpu    = "200m"
                            memory = "200Mi"
                        }
                    }

                    args = [
                        "--providers.kubernetescrd",
                        "--certificatesresolvers.myresolver.acme.email=andreas.askholm@gmail.com",
                        "--certificatesResolvers.myresolver.acme.dnsChallenge.disablePropagationCheck=true",
                        "--certificatesresolvers.myresolver.acme.dnschallenge.provider=duckdns",
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
                        "--log.level=ERROR"
                    ]

                    env {
                        name  = "DUCKDNS_TOKEN"
                        value = data.google_secret_manager_secret_version.duckdns_token.secret_data
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
                }
            }
        }
    }
}

resource "kubernetes_service" "traefik_websec_service" {
    metadata {
        name = "traefik-websec-service"
        namespace = "NAMESPACE_NAME"
    }

    spec {
        type = "LoadBalancer"

        port {
            name        = "https"
            port        = 443
            target_port = "websecure"
        }

        port {
            name        = "http"
            port        = 80
            target_port = "web"
        }

        selector = {
            app = "traefik"
        }
    }
}