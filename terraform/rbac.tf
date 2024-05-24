// Kubernetes Cluster Role for Traefik
resource "kubernetes_cluster_role" "traefik_role" {
    metadata {
        name = "traefik-ingress-controller"
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

    rule {
        api_groups = ["traefik.io"]
        resources  = ["middlewares", "middlewaretcps", "ingressroutes", "traefikservices", "ingressroutetcps", "ingressrouteudps", "tlsoptions", "tlsstores", "serverstransports", "serverstransporttcps"]
        verbs      = ["get", "list", "watch"]
    }
}

// Kubernetes Cluster Role Binding for Traefik
resource "kubernetes_cluster_role_binding" "traefik_role_binding" {
    metadata {
        name = "traefik-ingress-controller"
    }

    role_ref {
        api_group = "rbac.authorization.k8s.io"
        kind      = "ClusterRole"
        name      = kubernetes_cluster_role.traefik_role.metadata[0].name
    }

    subject {
        kind      = "ServiceAccount"
        name      = "traefik-ingress-controller"
        namespace = "NAMESPACE_NAME"
    }
}