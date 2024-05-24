variable "secrets_GUI" {
    description = "List of secrets to fetch from Google Secret Manager"
    type        = list(string)
    default     = ["SECRET_KEY", "ALLOWED_HOSTS", "CSRF_TRUSTED", "SU_PASSWORD", "SU_USER", "SU_EMAIL", "DB_ENGINE", "DB_USERNAME", "DB_PASSWORD", "DB_HOST", "DB_PORT", "CON_STORE", "MEDIA_PATH"]
}

data "google_secret_manager_secret_version" "secrets_GUI" {
    count   = length(var.secrets_GUI)
    secret  = format("%s_%s", var.namespace_name, var.secrets_GUI[count.index])
    version = "latest"
}

resource "kubernetes_secret" "gui_secrets" {
    count = length(var.secrets_GUI)

    metadata {
        name = format("gui-%s", lower(replace(var.secrets_GUI[count.index], "_", "-")))
        namespace = "NAMESPACE_NAME"
    }

    data = {
        (var.secrets_GUI[count.index]) = data.google_secret_manager_secret_version.secrets_GUI[count.index].secret_data
    }
}
// Kubernetes Deployment for GUI
resource "kubernetes_deployment" "gui_deployment" {
    metadata {
        name = "gui"
        namespace = "NAMESPACE_NAME"
        labels = {
            app  = "django"
            task = "gui"
        }
    }

    spec {
        replicas = 1

        selector {
            match_labels = {
                app  = "django"
                task = "gui"
            }
        }

        template {
            metadata {
                labels = {
                    app  = "django"
                    task = "gui"
                }
            }

            spec {
                volume {
                    name = "media-data"

                    persistent_volume_claim {
                        claim_name = "media-vol"
                    }
                }
                image_pull_secrets {
                    name = kubernetes_secret.docker_registry.metadata[0].name
                }

                container {
                    name  = "gui"
                    image = "europe-north1-docker.pkg.dev/devsecopsexamproject/exam-project/ui:latest"
                    

                    resources {
                        limits = {
                            cpu    = "1"
                            memory = "1Gi"
                        }
                        requests = {
                            cpu    = "500m"
                            memory = "400Mi"
                        }
                    }

                    port {
                        name           = "incomming"
                        container_port = 8000
                    }

                    volume_mount {
                        mount_path = "/var/www/media"
                        name       = "media-data"
                    }

                    dynamic "env" {
                        for_each = var.secrets_GUI
                        content {
                            name = env.value
                            value_from {
                                secret_key_ref {
                                    name = format("gui-%s", lower(replace(env.value, "_", "-")))
                                    key  = env.value
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

// Kubernetes Service for GUI
resource "kubernetes_service" "gui_service" {
    metadata {
        name = "gui"
        namespace = "NAMESPACE_NAME"
    }

    spec {
        selector = {
            app  = "django"
            task = "gui"
        }

        port {
            name        = "gui-access"
            port        = 8000
            target_port = "incomming"
        }
    }
}