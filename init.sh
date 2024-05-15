#!/bin/bash

# Initializs the Postgres database in kubernetes
# Create a 10GB disk in Google Cloud
gcloud compute disks create --size=10GB --zone=europe-west10-a postgres-disk

# Apply the StorageClass and PersistentVolume 
kubectl apply -f sc.yaml
kubectl apply -f pg-storage.yaml

# Apply the StatefulSet
kubectl apply -f statefulset.yaml