# Writing a Kubernetes Webhook in Python

## What is a webhook?

!!! note 

    I'll only briefly describe what a webhook is in the context of this
    document below but for detailed information see the kubernetes documentation on
    [Dynamic Admission Control]

A webhook is a way to validate and/or apply defaults
to a resource manifest such as a pod. Setting up a webhook typically requires a web
service (deployed on the cluster in the normal way) and some configuration
to tell Kubernetes how to use the web service. Those configurations are

* [MutatingWebhookConfiguration]
* [ValidatingWebhookConfiguration]

You can think of a webhook as a man in the middle attack on your
resource manifest on its way to [etcd].

``` mermaid
graph LR
    A[kubectl apply ...];
    B(Mutating Webhook);
    C(Validating Webhook);
    D[etcd];
    E[API Server];
    A --> E --> D;
    E --> |admission review| B;
    E --> |admission review| C;
    B --> |patch| E;
    C --> |allowed?| E;
    subgraph client
    A
    end
    subgraph cluster
    B
    C
    D
    E
    end
```

The client with POST a resource manifest to the Kubernetes API server such as 

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: http-server
spec:
  containers:
  - name: http-server
    image: python:3.9-slim
    command: ["python", "-m", "http.server", "8888"]
    ports:
    - name: http
      containerPort: 8888
```

Kubernetes will forward an admission review
to all applicable webhooks. The webhooks will respond with either patches
or allow/deny. Eventually Kubernetes will persist the resource.

<!--
this is a comment
-->

### Mutating (Defaulting) Webhook

A mutating webhook would apply defaults to a resource triggered by some event.
Let's say we wanted to add the image pull secret `registry-credentials` to every pod created in the default
namespace.

Using a mutating webhook, we can turn this

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: http-server
spec:
  containers:
    - name: http-server
      image: python:3.9-slim
      command: ["python", "-m", "http.server", "8888"]
      ports:
        - name: http
          containerPort: 8888
```
into this

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: http-server
spec:
  containers:
    - name: http-server
      image: python:3.9-slim
      command: ["python", "-m", "http.server", "8888"]
      ports:
        - name: http
          containerPort: 8888
  imagePullSecrets:
  - name: registry-credentials
```

### Validating Webhook
A validating webhook doesn't make any changes to the manifest. Its only
job is to assert on the validity of the resource. A common use case for
this is validating the image. If only images from a specific registry
such as `registry.example.com` are allowed (e.g. enterprise compliance requirements),
then we have the validating webhook
reject all pods with invalid references to those images.

#### Example - Creating a pod with a public image
```sh
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: http-server
spec:
  containers:
    - name: http-server
      image: python:3.9-slim
      command: ["python", "-m", "http.server", "8888"]
      ports:
        - name: http
          containerPort: 8888
EOF
```

### What are side effects?

## Why Python and not Go?

## Getting Started



[dynamic admission control]: https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/
[ValidatingWebhookConfiguration]: https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.23/#validatingwebhookconfiguration-v1-admissionregistration-k8s-io
[MutatingWebhookConfiguration]: https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.23/#mutatingwebhookconfiguration-v1-admissionregistration-k8s-io
[etcd]: https://kubernetes.io/docs/concepts/overview/components/#etcd