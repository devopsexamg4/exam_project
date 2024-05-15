// Kubernetes Cluster Role for Traefik
resource "kubernetes_cluster_role" "traefik_role" {
    metadata {
        name = "traefik-role"
    }

    rule {
        api_groups = [""]
        resources  = ["services", "endpoints", "secrets"]
        verbs      = ["get", "list", "watch"]
    }

    rule {
        api_groups = ["extensions", "networking.k8s.io"]
        resources  = ["ingresses", "ingressclasses"]
        verbs      = ["get", "list", "watch"]
    }

    rule {
        api_groups = ["extensions", "networking.k8s.io"]
        resources  = ["ingresses/status"]
        verbs      = ["update"]
    }
}

// Kubernetes Service Account for Traefik
resource "kubernetes_service_account" "traefik_account" {
    metadata {
        name      = "traefik-account"
        namespace = "default"
    }
}

// Kubernetes Cluster Role Binding for Traefik
resource "kubernetes_cluster_role_binding" "traefik_role_binding" {
    metadata {
        name = "traefik-role-binding"
    }

    role_ref {
        api_group = "rbac.authorization.k8s.io"
        kind      = "ClusterRole"
        name      = kubernetes_cluster_role.traefik_role.metadata[0].name
    }

    subject {
        kind      = "ServiceAccount"
        name      = kubernetes_service_account.traefik_account.metadata[0].name
        namespace = "default"
    }
}

// Kubernetes Cluster Role Binding for Default Role
resource "kubernetes_cluster_role_binding" "default_role_binding" {
    metadata {
        name = "default-role-binding"
    }

    role_ref {
        api_group = "rbac.authorization.k8s.io"
        kind      = "ClusterRole"
        name      = kubernetes_cluster_role.traefik_role.metadata[0].name
    }

    subject {
        kind      = "ServiceAccount"
        name      = "default"
        namespace = "default"
    }
}