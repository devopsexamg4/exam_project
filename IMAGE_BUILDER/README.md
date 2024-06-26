# Kaniko to build images from a dockerfile
## How to include
To use the image builder:
- copy the files ```__init__.py, kaniko.yml, podmanager.py, requirements.txt``` into your application,</br>be sure not to overwrite any files in your application.
- In your application set the environment variable ```CON_STORAGE``` to be the path/url to your container storage.
- Install the requirements with ```pip install -r requirements.txt```
- import the functions into your applications like you would any other import in python e.g. ```import podmanager as pm```
---
- In the case of the GUI application, copy the files into ```GUI/UI/frontend/img/*``` as specified in the ```/builder_to_gui.sh``` (or simply execute the script)
---
## How to use
All operations will be performed in namespace "default" on the cluster it is run</br>
To build an image:
```python
manifest = build_kaniko(dockerfile, image_name, tag=latest)
api_response = deploy_pod(manifest)
```
To start a job e.g. to evaluate a submission:
```python
resource_dict = {'maxmemory':str(memory limit in Mi),
                  'maxcpu':str(cpu limit),
                  'timer':str(maximum execution time from jobstart),
                  'sub':str(path to folder containing assignment)}
api = create_api_instance()
job, name = create_job_object(jobname, jobimage, resources=resource_dict)
api_response = create_job(api, job)
```

To get the status of a job:
```python
api = create_api_instance()
name = <name returned from create_job_object>
api_response = get_job_status(api,name)
```

To delete a job:
```python
api = create_api_instance()
name = <name returned from create_job_object>
api_response = delete_job(api,name)
```

Update a runninng job:
```python
old_name = <name returned from initial create_job_object>
resource_dict = {'maxmemory':str(memory limit in Mi),
                  'maxcpu':str(cpu limit),
                  'timer':str(maximum execution time from jobstart),
                  'sub':str(path to folder containing assignment)}
api = create_api_instance()
job, new_name = create_job_object(jobname, jobimage, resources=resource_dict)
api_response = update_job(api,job,old_name)
```
## Doc from [kaniko](https://raw.githubusercontent.com/GoogleContainerTools/kaniko/main/README.md)
#### Running kaniko in a Kubernetes cluster

Requirements:

- Standard Kubernetes cluster (e.g. using
  [GKE](https://cloud.google.com/kubernetes-engine/))
- [Kubernetes Secret](#kubernetes-secret)
- A [build context](#kaniko-build-contexts)

##### Kubernetes secret

To run kaniko in a Kubernetes cluster, you will need a standard running
Kubernetes cluster and a Kubernetes secret, which contains the auth required to
push the final image.

To create a secret to authenticate to Google Cloud Registry, follow these steps:

1. Create a service account in the Google Cloud Console project you want to push
   the final image to with `Storage Admin` permissions.
2. Download a JSON key for this service account
3. Rename the key to `kaniko-secret.json`
4. To create the secret, run:

```shell
kubectl create secret generic kaniko-secret --from-file=<path to kaniko-secret.json>
```

_Note: If using a GCS bucket in the same GCP project as a build context, this
service account should now also have permissions to read from that bucket._

The Kubernetes Pod spec should look similar to this, with the args parameters
filled in:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: kaniko
spec:
  containers:
    - name: kaniko
      image: gcr.io/kaniko-project/executor:latest
      args:
        - "--dockerfile=<path to Dockerfile within the build context>"
        - "--context=gs://<GCS bucket>/<path to .tar.gz>"
        - "--destination=<gcr.io/$PROJECT/$IMAGE:$TAG>"
      volumeMounts:
        - name: kaniko-secret
          mountPath: /secret
      env:
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /secret/kaniko-secret.json
  restartPolicy: Never
  volumes:
    - name: kaniko-secret
      secret:
        secretName: kaniko-secret
```

This example pulls the build context from a GCS bucket. To use a local directory
build context, you could consider using configMaps to mount in small build
contexts.