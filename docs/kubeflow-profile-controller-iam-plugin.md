# Kubeflow's IAM Plugin

The following describes how to setup the profile controllers IAM plugin. For
those who don't know what the profile controller is, I'll give a brief description
[below](#profile-controller), but as a high level summation, the profile controller
IAM plugin helps to establish trust relationships between a service account (pod identity)
on an EKS cluster and any number of protected resources in AWS


## Profile Controller
[Kubeflow] is designed in such a way that each user is provided their own namespace.
The goal of these namespaces seems to be isolated environments as well is imposing
resource restrictions per user. This allows users to track their own cluster resources
e.g. configmaps, secrets, ... etc.



[Kubeflow]: https://www.kubeflow.org/docs/
