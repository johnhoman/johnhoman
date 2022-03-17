# Writing a Kubernetes Webhook in Python

## What is a webhook?

!!! note 

    I'll only briefly describe what a webhook is in the context of this
    document below but for detailed information see the kubernetes documentation on
    [Dynamic Admission Control]

A webhook is a way to validate and/or apply defaults
to a resource manifest such as a pod. Setting up a webhook typically requires a web
service (deployed on the cluster in the normal way) and some configuration
to tell Kubernetes how to use the web service. These configurations are

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
this is validating a container image. If only images from a specific registry
such as `registry.example.com` are allowed (e.g. corporate compliance requirements),
then we can have the validating webhook reject all pods with references to
from other registries.


```sh
jhoman@pop-os:~$ kubectl run http-server --image=python:3.7 -- python -m http.server 8888
```
:x: `Error from server: admission webhook "webhook.example.com" denied the request: Invalid image. Images must come from registry.example.com`

```sh
jhoman@pop-os:~$ kubectl run http-server --image={++registry.example.com++}/python:3.7 -- python -m http.server 8888
```
:white_check_mark: `pod/http-server created`


## Writing a Webhook

Any of the Python web frameworks should work but [fastapi] is likely
the easiest. There's a lot of good information in the docs so for anything specific
probably start there.


The following is a basic webhook endpoint that sets the image pull policy
in all containers of a pod to `Always` is unset. You can read more about a
container image pull policy [here](https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy).

!!! note 
    
    In practice this is unnecessary. Kubernetes will choose a sensible default
    based on the image tag if imagePullPolicy isn't specified

```python
--8<-- "docs_src/kubernetes/webhook/python/tutorial0001.py"
```

Let's take a deeper look at what's going on here.

```python hl_lines="13"
--8<-- "docs_src/kubernetes/webhook/python/tutorial0001.py"
```

`admission_review` is the payload sent by the Kubernetes API server that contains
the manifest contents. The manifest resides in `#!python admission_review["request"]["object"]`
and in this example it contains a `Pod`.

!!! note

    `#!python copy.deepcopy()` is used to avoid mutating the original object. The original
    needs to be preserved to compute the json patch

```python hl_lines="16-17"
--8<-- "docs_src/kubernetes/webhook/python/tutorial0001.py"
```

Here the webhook is setting default values on the spec. It's important
that a webhook doesn't override a user provided value and only sets a
value this isn't already set in the manifest. If, for example, there
was already an `imagePullPolicy` of `IfNotPreset` set on the `Pod` then
it would be impolite to ignore it and potentially dangerous (existing
values are probably set for reason).

```python hl_lines="19 22"
--8<-- "docs_src/kubernetes/webhook/python/tutorial0001.py"
```

The response is a base64 encoded [json patch] with the changes
rather than the actual changed manifest. Which is basically signaling to
Kubernetes that the only fields that you care about are the fields
within the patch.


[dynamic admission control]: https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/
[ValidatingWebhookConfiguration]: https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.23/#validatingwebhookconfiguration-v1-admissionregistration-k8s-io
[MutatingWebhookConfiguration]: https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.23/#mutatingwebhookconfiguration-v1-admissionregistration-k8s-io
[etcd]: https://kubernetes.io/docs/concepts/overview/components/#etcd
[fastapi]: https://fastapi.tiangolo.com/
[json patch]: https://datatracker.ietf.org/doc/html/rfc6902