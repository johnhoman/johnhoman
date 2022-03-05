# Kubeflow's IAM Plugin

The following describes how to setup the profile controllers IAM plugin. For
those who don't know what the profile controller is, I'll give a brief description
[below](#profile-controller), but as a high level summation, the profile controller
IAM plugin helps to establish trust relationships between a service account (pod identity)
on an EKS cluster and any number of protected resources in AWS


## Profile Controller
[Kubeflow] is designed in such a way that each user is provided their own namespace.
During [user onboarding] a custom resource called a `Profile` is created for the 
user. This profile is created by a service called KFAM and managed by the profile controller. The profile controller manages several other resources as well, some of which are

* Namespace
* RoleBinding
* ServiceAccount
    - default-viewer - namespace read
    - default-editor - namespace write
* AuthorizationPolicy

For now we're going to ignore most of those things and focus on the service account. On
EKS clusters the service account is the identity that can assume a roles. There's some
setup required to make that statement trust but just to keep it simple, a pod that uses
a service account tagged with a role-arn can assume that role.



TODO: Finish


[Kubeflow]: https://www.kubeflow.org/docs/
[user onboarding]: https://www.kubeflow.org/docs/components/multi-tenancy/getting-started/#onboarding-a-new-user
