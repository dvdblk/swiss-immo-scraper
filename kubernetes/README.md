## Deployment to k8s

```
$ kubectl apply -k .
```

### Generating dockerconfig.json

For docker username use the github username, password is a [PAT](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry).

```
$ kubectl create secret docker-registry ghcr-regcred --docker-server=ghcr.io --docker-username=<username> --docker-password=<pw>
...
$ kubectl get secrets/ghcr-regcred -o jsonpath="{.data.\.dockerconfigjson}" -n immo-scraper | base64 -d > dockerconfig.json
```