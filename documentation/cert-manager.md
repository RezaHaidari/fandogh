# How to Setup cert-manager?    


## Things to remember

1. These are what cert-manager will do, so don't expect anything more:

    - Communicates with an ACME compatible issuer( like LetsEncrypt) to obtain a certificate.
    - Solve HTTP-01 and DNS-01 challenges
    - Store certificates in k8s secrets, (It doesnt automatically configure ingress with certificates)
    - Renew certificates automatically

2. cert-manager solves HTTP-01 in this way:     
I. fires up an ingress on the specific path  
II. keep that ingress up until validation get completed   
III. cleanup that ingress

3. cert-manager doesnt't support digital ocean API in order to be able to solve DNS-01 challenges at the moment, but there is a PR open here:
https://github.com/jetstack/cert-manager/pull/345

4. We can't get wildcard certificate if we can't solve DNS-01 challenges

## cert-manager Installation

### Step1: Install Helm
You can get helm binaries from [Here](https://github.com/kubernetes/helm/releases), extract them and run:
```bash
./helm init
```
And let's test it:
```bash
./helm list
```
You might face `port forwarding` error which will be fixed by installing socot on all nodes:
```bash
apt-get install socat
```


### Step2: Install cert-manager using helm

Simple as running:
```bash
helm install \
    --name cert-manager \
    --namespace kube-system \
    stable/cert-manager
```

### Step3: Define Let's Encrypt ClusterIssuer:
it's something like this:
```yaml
apiVersion: certmanager.k8s.io/v1alpha1
kind: ClusterIssuer
metadata:
  name: letsencrypt
spec:
  acme:
    # The ACME server URL
    server: https://acme-v02.api.letsencrypt.org/directory
    # Email address used for ACME registration
    email: Your-email@somewhere.com
    # Name of a secret used to store the ACME account private key
    privateKeySecretRef:
      name: letsencrypt
    # Enable the HTTP-01 challenge provider
    http01: {}
```
it's a ClusterIssuer, which you can use it from any namespace
for testing purposes it's better to use letsencrypt staging API by changing server to `https://acme-staging-v02.api.letsencrypt.org/directory`

### Step4: Create Certificate

As soon as you create Certificate, cert-manager starts trying to get a certificate from Issuer, it doesn't need anything else:
```yaml
apiVersion: certmanager.k8s.io/v1alpha1
kind: Certificate
metadata:
  name: roozameh-net
  namespace: default
spec:
  secretName: roozameh-net-tls
  issuerRef:
    name: letsencrypt
    kind: ClusterIssuer
  commonName: roozameh.net
  dnsNames:
  - roozameh.net
  acme:
    config:
    - http01:
        ingressClass: nginx
      domains:
      - roozameh.net
```
after doing this, go get the cert-manager pod id and check the logs to see how it goes, if everything goes well 
cert-manager should creates new secret for your certificate:

```bash
kubectl get secrets -n [namespace]
``` 

if you got an error in logs like `self check failed` that means letsencrypt validation got failed,
