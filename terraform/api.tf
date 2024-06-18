variable "secrets_API" {
    description = "List of secrets to fetch from Google Secret Manager"
    type        = list(string)
    default     = ["DB_PORT", "DB_HOST", "DB_NAME", "ADMIN_USERNAME", "ADMIN_PASSWORD","API_SECRET","CON_STORE"]
}

variable "env_var_mapping_API" {
    description = "Mapping of secret names to environment variable names"
    type        = map(string)
    default     = {
        "DB_USERNAME" = "DB_USER",
        "DB_PASSWORD" = "DB_PASSWORD",
        "DB_PORT"     = "DB_PORT",
        "DB_HOST"     = "DB_HOST",
        "DB_NAME"     = "DB_NAME",
        "ADMIN_USERNAME" = "ADMIN_USERNAME",
        "ADMIN_PASSWORD" = "ADMIN_PASSWORD",
        "API_SECRET"    = "SECRET_KEY"
    }
}

data "google_secret_manager_secret_version" "secrets_API" {
    count   = length(var.secrets_API)
    secret  = format("%s_%s", var.namespace_name, var.secrets_API[count.index])
    version = "latest"
}

resource "kubernetes_secret" "API_secrets" {
    count = length(var.secrets_API)

    metadata {
        name = lower(replace(var.secrets_API[count.index], "_", "-"))
        namespace = "NAMESPACE_NAME"
    }

    data = {
        (var.secrets_API[count.index]) = data.google_secret_manager_secret_version.secrets_API[count.index].secret_data
    }
}

resource "kubernetes_deployment" "api_deployment" {
    metadata {
        name = "api"
        namespace = "NAMESPACE_NAME"
        labels = {
            app  = "fastapi"
            task = "api"
        }
    }

    spec {
        replicas = 1

        selector {
            match_labels = {
                app  = "fastapi"
                task = "api"
            }
        }

        template {
            metadata {
                labels = {
                    app  = "fastapi"
                    task = "api"
                }
            }

            spec {
                image_pull_secrets {
                    name = kubernetes_secret.docker_registry.metadata[0].name
                }
                container {
                    name  = "api"
                    image = "europe-north1-docker.pkg.dev/devsecopsexamproject/exam-project/api:latest"

                    
                    resources {
                        limits = {
                            cpu    = "1"
                            memory = "1Gi"
                        }
                        requests = {
                            cpu    = "250m"
                            memory = "400Mi"
                        }
                    }

                    port {
                        name           = "incomming"
                        container_port = 8000
                    }

                    dynamic "env" {
                        for_each = var.secrets_API
                        content {
                        name = var.env_var_mapping_API[env.value]
                        value_from {
                            secret_key_ref {
                            name = lower(replace(env.value, "_", "-"))
                            key  = env.value
                            }
                        }
                        }
                    }
                    env {
                        name = "DB_USER"
                        value_from {
                            secret_key_ref {
                                name = "db-username"
                                key  = "DB_USERNAME"
                            }
                        }
                    }

                    env {
                        name = "DB_PASSWORD"
                        value_from {
                            secret_key_ref {
                                name = "db-password"
                                key  = "DB_PASSWORD"
                            }
                        }
                    }

                }
            }
        }
    }
}

resource "kubernetes_service" "api_service" {
    metadata {
        name = "api"
        namespace = "NAMESPACE_NAME"
    }

    spec {
        selector = {
            app  = "fastapi"
            task = "api"
        }

        port {
            name        = "api-access"
            port        = 8000
            target_port = "incomming"
        }
    }
}
