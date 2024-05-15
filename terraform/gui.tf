// Kubernetes Deployment for GUI
resource "kubernetes_deployment" "gui_deployment" {
    metadata {
        name = "gui"
        labels = {
            app = "gui"
        }
    }

    spec {
        replicas = 1

        selector {
            match_labels = {
                app = "gui"
            }
        }

        template {
            metadata {
                labels = {
                    app = "gui"
                }
            }

            spec {
                container {
                    name  = "gui"
                    image = "europe-north1-docker.pkg.dev/devsecopsexamproject/exam-project/ui:latest"

                    port {
                        name           = "incomming"
                        container_port = 8000
                    }
                }

                image_pull_secrets {
                    name = "regcred"
                }
            }
        }
    }
}

// Kubernetes Service for GUI
resource "kubernetes_service" "gui_service" {
    metadata {
        name = "gui-service"
    }

    spec {
        selector = {
            app = "gui"
        }

        port {
            name        = "websecure"
            port        = 443
            target_port = "incomming"
        }
    }
}