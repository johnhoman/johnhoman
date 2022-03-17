# main.py
import copy
from base64 import b64encode

from fastapi import FastAPI
from jsonpatch import JsonPatch

app = FastAPI()


@app.post("/mutate-v1-pod")
def mutate_pod(admission_review: dict):
    pod = copy.deepcopy(admission_review["request"]["object"])
    containers = pod["spec"]["containers"]

    for k in range(0, len(containers)):
        containers[k].setdefault("imagePullPolicy", "Always")

    patch = JsonPatch.from_diff(admission_review["request"]["object"], pod)
    admission_review["response"] = {
        "uid": admission_review["request"]["uid"],
        "patch": b64encode(str(patch).encode()).decode(),
        "patchType": "JSONPatch",
    }
    return admission_review
