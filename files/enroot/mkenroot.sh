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

__docker_image="${1}"

__sqsh_name=$(echo "${__docker_image}" | sed -E -e "s|^(gitlab-master\.nvidia\.com\/)([a-zA-Z\-\_\.]+\/)||" -e "s|[\/:]|-|g")
__sqsh_name="${STORE_HOME}/images/${__sqsh_name}"

enroot remove -f "$(basename "${__sqsh_name}")"
rm -f "${__sqsh_name}.sqsh"

enroot import -o "${__sqsh_name}.sqsh" "docker://${__docker_image}"
enroot create "${__sqsh_name}.sqsh"
