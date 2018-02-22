# Kubernetes Python client CRD example

The example is based on the CRD here: https://kubernetes.io/docs/tasks/access-kubernetes-api/extend-api-custom-resource-definition

## Python client installation

```bash
sudo -H pip3 install -U kubernetes==v5.0.0
```

## Execute example

```bash
python3 main.py
```

in another terminal window:

```bash
kubectl apply -f my-crontab.yaml
```
