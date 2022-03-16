# main.py
from base64 import b64encode

from fastapi import FastAPI
from jsonpatch import JsonPatch

app = FastAPI()


@app.post("/mutate-v1-pod")
def mutate_pod(admission_review: dict):
    pod = admission_review["request"]["object"]
    containers = pod["spec"]["containers"]
    for k in range(0, len(containers)):
        containers[k].setdefault("imagePullPolicy", "Always")
    pod["spec"]["containers"] = containers
    patch = JsonPatch.from_diff(admission_review["request"]["object"], pod)
    return {
        "response": {
            "uid": admission_review["request"]["uid"],
            "patch": b64encode(str(patch).encode()).decode(),
            "patchType": "JSONPatch",
        }
