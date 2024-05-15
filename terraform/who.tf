resource "kubernetes_deployment" "whoami_deployment" {
    metadata {
        name = "whoami"
        labels = {
            app = "whoami"
        }
    }

    spec {
        replicas = 1
        selector {
            match_labels = {
                app = "whoami"
            }
        }

        template {
            metadata {
                labels = {
                    app = "whoami"
                }
            }

            spec {
                container {
                    name  = "whoami"
                    image = "traefik/whoami"

                    port {
                        name           = "web"
                        container_port = 80
                    }
                }
            }
        }
    }
}

resource "kubernetes_service" "whoami_service" {
    metadata {
        name = "whoami"
    }

    spec {
        selector = {
            app = "whoami"
        }

        port {
            name        = "websecure"
            port        = 443
            target_port = "web"
        }
    }
}
