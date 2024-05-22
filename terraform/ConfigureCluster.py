import os
import sys

files = ["kubernetes.tf", "gui.tf", "traefik.tf", "rbac.tf", "db.tf", "api.tf"]

def applyChange(clusterName, namespace):
    print("Changing cluster name to: " + clusterName)
    print("Changing namespace to: " + namespace)
    for fileName in files:
        print("Changing file: " + fileName)
        with open(fileName, "r") as file:
            filedata = file.read()

        with open((fileName + "_bak"), "w") as file:
            file.write(filedata)

        # Replace the target string
        filedata = filedata.replace("CLUSTER_NAME", clusterName)
        filedata = filedata.replace("NAMESPACE_NAME", namespace)
        
        # Write the file out again
        with open(fileName, "w") as file:
            file.write(filedata)
        print("File changed: " + fileName)
    

def deapplyChange():
    for fileName in files:
        with open((fileName + "_bak"), "r") as file:
            filedata = file.read()

        with open(fileName, "w") as file:
            file.write(filedata)

        # remove backup file
        os.remove((fileName + "_bak"))

if __name__ == '__main__':
    if len(sys.argv) > 3 and sys.argv[1] == "apply":
        applyChange(sys.argv[2], sys.argv[3])
    else:
        deapplyChange()