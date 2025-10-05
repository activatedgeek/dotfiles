#!/usr/bin/env bash

##
# Usage:
#   mkenroot.sh [docker/image:tag]
#

if [[ -z "${1}" ]]; then
    echo "Missing Docker image."
    echo "Usage: mkenroot.sh [docker/image:tag]"
    exit 1
fi

mkdir -p ${STORE_HOME}/images

image="${1}"

sqsh_name=$(echo "${image}" | sed -E -e 's|^(gitlab\-master\.nvidia\.com\/\|nvcr\.io\/)([a-zA-Z\-\_\.]+\/)||' -e 's|[\/:]|-|g')
sqsh_name="${STORE_HOME}/images/${sqsh_name}"

enroot remove -f "$(basename "${sqsh_name}")"
rm -f "${sqsh_name}.sqsh"

enroot import -o "${sqsh_name}.sqsh" "docker://${image}"
enroot create "${sqsh_name}.sqsh"
