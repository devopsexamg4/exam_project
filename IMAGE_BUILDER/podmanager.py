"""
This module is used to interact with our kubernetes cluster.
images can be build from dockerfiles with kaniko
https://github.com/GoogleContainerTools/kaniko

images can be deployed using python-kubernetes
https://github.com/kubernetes-client/python
"""
from uuid import uuid4

import yaml
from decouple import config as env
from kubernetes import client, config, utils
from kubernetes.utils.create_from_yaml import FailToCreateError

def build_kaniko(dockerfile: str, name: str, tag: str='latest') -> dict:
    """
    modify the kaniko template to build an image from the given dockerfile
    and push it to the container storage defined in environment variable CON_STORE
    """
    # open kaniko template
    with open("kaniko.yml",'r', encoding='utf-8') as kan:
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

if __name__ == '__main__':
    import sys
    argv = sys.argv

    if ('--test' or '-t') in argv:
        test = []
        for _ in range(100):
            uid = [str(uuid4().hex)[:10] for _ in range(40000)]
            test.append(len(uid)==len(list(set(uid))))
        print(False not in test)

    
    
    man = build_kaniko('df', 'awesome', tag='v4')
    deploy_pod(man)