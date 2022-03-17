import base64
import json

from tutorial0001 import app
from fastapi.testclient import TestClient


ar = {
    "kind": "AdmissionReview",
    "apiVersion": "admission.k8s.io/v1beta1",
    "request": {
        "uid": "0df28fbd-5f5f-11e8-bc74-36e6bb280816",
        "kind": {"group": "", "version": "v1", "kind": "Pod"},
        "resource": {"group": "", "version": "v1", "resource": "pods"},
        "namespace": "dummy",
        "operation": "CREATE",
        "userInfo": {
            "username": "system:serviceaccount:kube-system:replicaset-controller",
            "uid": "a7e0ab33-5f29-11e8-8a3c-36e6bb280816",
            "groups": [
                "system:serviceaccounts",
                "system:serviceaccounts:kube-system",
                "system:authenticated",
            ],
        },
        "object": {
            "metadata": {
                "name": "test-pod",
                "namespace": "testspace-1234",
            },
            "spec": {
                "volumes": [],
                "containers": [
                    {
                        "name": "main",
                        "image": "python:3.8",
                    },
                    {
                        "name": "proxy",
                        "image": "nginx:latest",
                    },
                ],
                "restartPolicy": "Always",
                "serviceAccountName": "default",
                "serviceAccount": "default",
            },
            "status": {},
        },
        "oldObject": None,
    },
}


def test_response():
    client = TestClient(app)

    resp = client.post("/mutate-v1-pod", json=ar)
    assert resp.json()["response"]
    patch = resp.json()["response"]["patch"]
    decoded = base64.b64decode(patch)
    patches = {}
    for item in json.loads(decoded):
        patches[item["path"]] = item["value"]

    assert "/spec/containers/0/imagePullPolicy" in patches
    assert "/spec/containers/1/imagePullPolicy" in patches
