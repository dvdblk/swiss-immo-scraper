## Deployment to k8s

```
# Set up your .env file in the root of the repo
# Then create a hard link
$ ln ../.env .env
# Then apply the resources with kustomize
$ kubectl apply -k .
```