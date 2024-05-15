import subprocess

def run_command(command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        if error:
                print(f"Error: {error}")
        else:
                print(output)

# Create ingress using kubectl
ingress_yaml = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
    name: whoami-ingress
    namespace: default
spec:
    ingressClassName: gce
    rules:
        - host: devg4.duckdns.org
          http:
            paths:
                - path: /*
                  pathType: Prefix
                  backend:
                    service:
                        name: whoami-service
                        port:
                            number: 80
"""

with open("who_ingress.yaml", "w") as file:
        file.write(ingress_yaml)

run_command("kubectl apply -f who_ingress.yaml")
# Create ingress using kubectl
ingress_yaml = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
    name: gui-ingress
spec:
    ingressClassName: gce
    rules:
        - host: devg4.duckdns.org
          http:
            paths:
                - path: /
                  pathType: Prefix
                  backend:
                    service:
                        name: gui-service
                        port:
                            number: 443
"""

with open("gui_ingress.yaml", "w") as file:
        file.write(ingress_yaml)

run_command("kubectl apply -f gui_ingress.yaml")