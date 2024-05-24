#!/bin/bash

CLUSTER_NAME=$1
ZONE="europe-north1-a"
PROJECT_ID="devsecopsexamproject"
NAMESPACE=$2

if [ -z "$CLUSTER_NAME" ]; then
    CLUSTER_NAME="gke-cluster"
fi

if [ -z "$NAMESPACE" ]; then
    NAMESPACE="default"
fi

echo "Cluster Name: $CLUSTER_NAME"

gcloud auth activate-service-account --key-file=credentials.json
gcloud config set project $PROJECT_ID
terraform init -reconfigure -upgrade

terraformState=$(terraform state list)
if [[ $terraformState == *"google_container_cluster.primary"* ]]; then
    terraform state rm google_container_cluster.primary
fi

echo "Creating GKE Cluster"
pip install google-cloud-container kubernetes
python createCluster.py $CLUSTER_NAME

while true; do
    clusterStatus=$(gcloud container clusters describe $CLUSTER_NAME --zone $ZONE --project $PROJECT_ID --format="value(status)")
    echo "Current cluster status: $clusterStatus"
    if [ "$clusterStatus" == "PROVISIONING" ]; then
        sleep 10
    else
        break
    fi
done

gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE --project $PROJECT_ID
helm repo add traefik https://containous.github.io/traefik-helm-chart
helm repo update
echo "Setting up secrets"

declare -A secrets
if [ -f "secrets.json" ]; then
    secrets=$(jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' secrets.json)
fi

keys=("SECRET_KEY" "DEBUG" "ALLOWED_HOSTS" "CSRF_TRUSTED" "SU_PASSWORD" "SU_USER" "SU_EMAIL" "DB_ENGINE" "DB_USERNAME" "DB_PASSWORD" "CON_STORE" "DB_PORT" "DB_NAME")

for key in "${keys[@]}"; do
    value=${secrets[$key]}
    if [ -z "$value" ]; then
        read -p "Enter value for $key: " value
    fi

    namespacedKey="${NAMESPACE}_$key"

    if ! gcloud secrets describe $namespacedKey >/dev/null 2>&1; then
        gcloud secrets create $namespacedKey --replication-policy="user-managed" --locations="europe-north1"
    fi

    tempFile=$(mktemp)
    echo $value > $tempFile

    gcloud secrets versions add $namespacedKey --data-file="$tempFile"

    rm $tempFile
done

if ! gcloud secrets describe "${NAMESPACE}_DB_HOST" >/dev/null 2>&1; then
    gcloud secrets create "${NAMESPACE}_DB_HOST" --replication-policy="user-managed" --locations="europe-north1"
fi

tempFile=$(mktemp)
echo "db-service.$NAMESPACE.svc.cluster.local" > $tempFile

gcloud secrets versions add "${NAMESPACE}_DB_HOST" --data-file="$tempFile"

rm $tempFile

echo "Setup disks"
diskNames=("media-disk" "traefik-disk" "db-disk")
for diskName in "${diskNames[@]}"; do
    gcloud compute disks create $diskName \
        --size=10GB \
        --zone=europe-north1-a \
        --type=pd-standard \
        --labels=environment=dev
done

echo "Creating or updating service account: traefik-ingress-controller, and creating traefik-vol and media-vol"
kubectl apply -f volumesAndIngressAccount.yml --namespace=$NAMESPACE

echo "Installing Traefik"
kubectl apply -f ../traefik/00-rdef.yml --namespace=$NAMESPACE
python ConfigureCluster.py "apply" $CLUSTER_NAME $NAMESPACE
terraform import kubernetes_cluster_role.traefik_default traefik-default
terraform apply -auto-approve -refresh=false
python ConfigureCluster.py

echo "Creating ingress"
kubectl apply -f ../traefik/03-ingressroutes.yml --namespace=$NAMESPACE