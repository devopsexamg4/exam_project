terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.29.0"
    }
    http = {
      source  = "hashicorp/http"
      version = "~> 2.1.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.5.0"
    }
  }
}

data "google_client_config" "default" {}

provider "google" {
  credentials = file("credentials.json")
  project     = "devsecopsexamproject"
  region      = "europe-north1-a"
}

data "google_container_cluster" "primary" {
  name     =  "CLUSTER_NAME"
  location =  "europe-north1-a"
}

resource "kubernetes_secret" "docker_registry" {
  metadata {
    name = "regcred"
  }

  data = {
    ".dockerconfigjson" = jsonencode({
      "auths" = {
        "europe-north1-docker.pkg.dev" = {
          "username" = "_json_key"
          "password" = file("credentials.json")
        }
      }
    })
  }

  type = "kubernetes.io/dockerconfigjson"
}

resource "kubernetes_secret" "traefik_dns_acc" {
  metadata {
    name = "traefik-dns-acc"
    namespace = "NAMESPACE_NAME"
  }

  data = {
    "your-secret-key" = file("credentials.json")
  }

  type = "Opaque"
}
data "google_project" "current" {}

resource "kubernetes_secret" "gcloud_project" {
  metadata {
    name = "gcloud-project"
    namespace = "NAMESPACE_NAME"
  }

  data = {
    "project" = base64encode(data.google_project.current.project_id)
  }

  type = "Opaque"
}

provider "kubernetes" {
  config_path = null

  host  = "https://${data.google_container_cluster.primary.endpoint}"
  token = data.google_client_config.default.access_token

  client_certificate     = base64decode(data.google_container_cluster.primary.master_auth[0].client_certificate)
  client_key             = base64decode(data.google_container_cluster.primary.master_auth[0].client_key)
  cluster_ca_certificate = base64decode(data.google_container_cluster.primary.master_auth[0].cluster_ca_certificate)

  experiments {
    manifest_resource = true
  }
}

resource "google_container_node_pool" "primary_preemptible_nodes" {
  name       = "CLUSTER_NAME"
  location   = "europe-north1-a"
  cluster    = data.google_container_cluster.primary.name
  node_count = 1

  node_config {
    preemptible  = true
    machine_type = "e2-small"

    disk_size_gb = 10
    disk_type    = "pd-standard"

    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }

    tags = ["CLUSTER_NAME"]
  }
}


resource "kubernetes_cluster_role" "traefik_default" {
  metadata {
    name = "traefik-default"
  }
  rule {
    api_groups = [""]
    resources  = ["endpoints", "services", "secrets"]
    verbs      = ["get", "list", "watch"]
  }
}

variable "namespace_name" {
    description = "Namespace name to append to each secret"
    type        = string
    default     = "NAMESPACE_NAME"
}