#!/bin/sh
script_dir=$(dirname "$0")
eval "$(jq -r '@sh "HOST=\(.host) TOKEN=\(.token) CACERT=\(.cluster_ca_certificate)"')"
CACERT_FILE=$(mktemp)
echo "${CACERT}" > "${CACERT_FILE}"

dostuff() {
    kubectl get pods --token="${TOKEN}" --server="${HOST}" --certificate-authority="${CACERT_FILE}" --namespace=webapp -o json
}


apply() {
    kubectl --token="${TOKEN}" --server="${HOST}" --certificate-authority="${CACERT_FILE}" --namespace=webapp delete deployment webapp-deployment2 2> results.txt
    sleep 5
    kubectl --token="${TOKEN}" --server="${HOST}" --certificate-authority="${CACERT_FILE}" --namespace=webapp apply -f $script_dir/web-app.yaml 
}

result=$(apply)
env_base64=$(dostuff | base64 | tr -d '\n')
echo "{\"myoutput\":\"${env_base64}\"}" | jq