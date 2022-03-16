# Kubeflow's IAM Plugin

The following describes how to setup the profile controllers IAM plugin. For
those who don't know what the profile controller is, I'll give a brief description
[below](#profile-controller), but as a high level summation, the profile controller
IAM plugin helps to establish trust relationships between a service account (pod identity)
on an EKS cluster and any number of protected resources in AWS


## Profile Controller
[Kubeflow] is designed in such a way that each user is provided their own namespace.
During [user onboarding] a custom resource called a `Profile` is created for the 
user. This profile is created by a service called KFAM and managed by the profile
controller. The profile controller manages several other resources as well, some of which are

* Namespace
* RoleBinding
* ServiceAccount
    - default-viewer - namespace read
    - default-editor - namespace write
* AuthorizationPolicy

For now we're going to ignore most of those things and focus on the service account.
A `ServiceAccount` in [Kubernetes] is a way for a pod to authenticate
with the Kubernetes api server. It can be used for various other things
(secret allowlisting, image pull secret injection, ..., etc). EKS uses a service
account as a trusted identity to access other AWS resources such as [s3].


### Annotating the ServiceAccount

You can either create a new service account with an annotation
or use an existing one provided by [Kubeflow]. For now I'll annotate
the default user for the [example installation].

```zsh
kubectl annotate sa/default-editor -n kubernetes-user-example-com eks.amazonaws.com/role-arn=arn:aws:iam::0123456789012:role/kubernetes-user
```

TODO: Finish


[s3]: https://docs.aws.amazon.com/s3/index.html
[Kubeflow]: https://www.kubeflow.org/docs/
[user onboarding]: https://www.kubeflow.org/docs/components/multi-tenancy/getting-started/#onboarding-a-new-user
[example installation]: https://github.com/kubeflow/manifests/tree/master/example
