import argparse
from google.cloud import container_v1
from google.cloud.container_v1.types import cluster_service
from kubernetes import client, config
import subprocess
import time

def create_cluster(project_id, zone, cluster_id):
    client = container_v1.ClusterManagerClient()

    # Check if the cluster already exists
    project_location = f"projects/{project_id}/locations/{zone}"
    request = cluster_service.ListClustersRequest(parent=project_location)
    clusters = client.list_clusters(request).clusters
    if any(cluster.name == cluster_id for cluster in clusters):
        print(f"Cluster {cluster_id} already exists.")
    else:
        # Specify the cluster configuration
        cluster = {
            'name': cluster_id,
            'initial_node_count': 3,  # Increase the number of nodes
            'master_auth': {'client_certificate_config': {'issue_client_certificate': False}},
            'node_config': {
                'machine_type': 'e2-small',  # Specify the machine type
                'disk_size_gb': 10,  # Specify the disk size in GB
                'disk_type': 'pd-standard',  # Specify the disk type
            },
        }

        # Create the cluster
        print(f"Creating cluster {cluster_id}...")
        cluster_request = cluster_service.CreateClusterRequest(parent=project_location, cluster=cluster)
        operation = client.create_cluster(cluster_request)
        print('Cluster creation operation: ', operation)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a GKE cluster.')
    parser.add_argument('cluster_name', type=str, help='The name of the GKE cluster to create.')

    args = parser.parse_args()
    create_cluster('devsecopsexamproject', 'europe-north1-a', args.cluster_name)
