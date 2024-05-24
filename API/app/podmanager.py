"""
This module is used to interact with our kubernetes cluster.
It is designed to run as a pod in the cluster it is performing operations in
if a 403 error occurs refer to: 
https://github.com/kubernetes-client/python/blob/master/examples/in_cluster_config.py

images can be build from dockerfiles with kaniko
https://github.com/GoogleContainerTools/kaniko

jobs are crud'ed(?) using python-kubernetes
https://github.com/kubernetes-client/python
"""
from uuid import uuid4

import yaml
from decouple import config as env
from pathlib import Path
from kubernetes import client, config, utils
from kubernetes.utils.create_from_yaml import FailToCreateError

DEFAULT_RESOURCE = {'maxmemory':'100',
                    'maxcpu':'1',
                    'timer':'120',
                    'sub':''}

def build_kaniko(dockerfile: str, name: str, tag: str='latest') -> dict:
    """
    modify the kaniko template to build an image from the given dockerfile
    and push it to the container storage defined in environment variable CON_STORE
    """
    # open kaniko template
    template = Path(__file__).with_name('kaniko.yml')
    with open(template,'r', encoding='utf-8') as kan:
        manifest = yaml.safe_load(kan)

    # get and replace the args
    args = manifest['spec']['containers'][0]['args']

    args[0] = args[0].replace('$DOCKERFILE',dockerfile)
    args[2] = args[2].replace('$STORE',env('CON_STORE'))
    args[2] = args[2].replace('$IMAGE',name)
    args[2] = args[2].replace('$TAG',tag)

    # put the args back into the manifest and return the manifest
    manifest['spec']['containers'][0] |= {'args':args}
    # create a unique name for the pod
    ident = str(uuid4().hex)[:10]
    manifest['spec']['containers'][0] |= {'name':f'kaniko-{ident}'}
    manifest['metadata'] |= {'name':f'kaniko-{ident}'}

    return manifest

def deploy_pod(manifest: dict) -> list:
    """
    deploy a pod to the cluster in which this module is running
    """
    config.load_incluster_config()
    k8s_client = client.ApiClient()
    try:
        api_resp = utils.create_from_dict(k8s_client, manifest)
    except FailToCreateError as e:
        api_resp = [e]

    return api_resp

def create_job_object(name:str, 
                      image: str, 
                      resources: dict=DEFAULT_RESOURCE) -> tuple:
    """
    create a job for kubernetes
    @param name, initial name for the job
            be aware an additional identifier will be appended before being returned
    @param image, The name of the image including the url on which it is hosted
    @param resources, A dictionary containing the resources
            the resources dict must contain four(4) key:value pairs:
            'maxcpu':int, limit to cpu
            'maxmemory':int, limit to memory
            'timer':int, limit runtime
            'sub':str, path to submission, without file name
    @return tuple(kubernetes.client.V1Job, str)
    """
    # Configureate Pod template container
    container = client.V1Container(
        name = name,
        image = image,
        command = ["./tester/run"],
        resources = client.V1ResourceRequirements(
            limits = {"cpu": resources['maxcpu'], 
                      "memory": f"{resources['maxmemory']}Mi"},
        ),
        volume_mounts = [client.V1VolumeMount(mount_path = '/assignment',
                                              name = 'assignment-data',
                                              sub_path = resources['sub'] ),
                         client.V1VolumeMount(mount_path = '/output',
                                              name = 'assignment-data',
                                              sub_path = resources['sub'] )]
    )

    # Claim containing the submissions
    claim = client.V1PersistentVolumeClaimVolumeSource(claim_name = 'media-vol')
    # Create and configure a spec section
    template = client.V1PodTemplateSpec(
        metadata = client.V1ObjectMeta(labels = {"app": name}),
        spec = client.V1PodSpec(containers = [container], 
                              volumes = [client.V1Volume(name = 'assignment-data', 
                                                       persistent_volume_claim = claim)]),
    )

    # Create the specification of job
    spec = client.V1JobSpec(template = template,
                            active_deadline_seconds = resources['timer'],
                            backoff_limit = 4)

    # Instantiate the job object
    name_id = f"{name}-{str(uuid4())[:10]}"
    job = client.V1Job(
        api_version = "batch/v1",
        kind = "Job",
        metadata = client.V1ObjectMeta(name = name_id),
        spec = spec,
    )

    return (job, name_id)

def create_api_instance() -> client.BatchV1Api:
    return client.BatchV1Api()

def create_job(api_instance: client.BatchV1Api, job: client.V1Job) -> client.V1Job:
    config.load_incluster_config()
    api_response = api_instance.create_namespaced_job(
        body = job,
        namespace = "default")
    
    return api_response

def get_job_status(api_instance: client.BatchV1Api, name: str) -> client.V1Job:
    api_response = api_instance.read_namespaced_job_status(
        name = name,
        namespace = "default")
    return api_response

def update_job(api_instance: client.BatchV1Api, job: client.V1Job, name: str) -> client.V1Job:
    api_response = api_instance.patch_namespaced_job(
        name = name,
        namespace = "default",
        body = job)
    return api_response

def delete_job(api_instance: client.BatchV1Api, name:str) -> client.V1Status:
    api_response = api_instance.delete_namespaced_job(
        name = name,
        namespace = "default",
        body = client.V1DeleteOptions(
            grace_period_seconds = 0,
        )
    )
    return api_response




if __name__ == '__main__':
    import sys
    argv = sys.argv

    if ('--test' in argv) or ( '-t' in argv):
        # unscientific 'test' of collisions in uuid
        # to determine the appropriate length of identifiers
        test = []
        for _ in range(100):
            uid = [str(uuid4().hex)[:10] for _ in range(40000)]
            test.append(len(uid)==len(list(set(uid))))
        assert False not in test, "There was a collision in the identifier test"

    # flow of operations 
    # if starting from a dockerfile use kaniko
    man = build_kaniko('df', 'awesome', tag='v4')
    res = deploy_pod(man)
    # get the image path/name
    img = man['spec']['containers'][0]['args'][2]
    # job creation using the python kubernetes module
    api = create_api_instance()
    job,name = create_job_object('GUI','europe-north1-docker.pkg.dev/devsecopsexamproject/exam-project/ui:latest')
    res = create_job(api,job)
    res = get_job_status(api,name)
    """ 
    update image before updating job
    if the image name changes create a new job but
        keep the old name returned from create_job_object
    """
    res = update_job(api, job, name)
    res = delete_job(api, name)
    
    
    