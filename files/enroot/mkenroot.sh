#!/usr/bin/env bash

##
# Usage:
#   mkenroot.sh <docker/image:tag> [output.sqsh]
#

if [[ -z "${1}" ]]; then
    echo "Missing Docker image."
    echo "Usage: mkenroot.sh [docker/image:tag]"
    exit 1
fi
image="${1}"

sqsh_name="${2}"
if [[ -z "${sqsh_name}" ]]; then
    echo "[WARNING] Missing squash name. Setting default."

    sqsh_name=$(echo "${image}" | sed -E -e 's|^(gitlab\-master\.nvidia\.com\/\|nvcr\.io\/)([a-zA-Z\-\_\.]+\/)||' -e 's|[\/:]|-|g')
    sqsh_name="${STORE_HOME}/images/${sqsh_name}.sqsh"
fi

echo "[INFO] Creating squash file \"${sqsh_name}\" for image \"${image}\"..."

mkdir -p "$(dirname "${sqsh_name}")"

export ENROOT_CACHE_PATH="$(dirname "${sqsh_name}")/.cache/enroot"
export SQSH_CACHE_DIR="$(dirname "${sqsh_name}")/.cache/sqsh"
export ENROOT_DATA_PATH="$(dirname "${sqsh_name}")/.cache/enroot-data"

enroot remove -f "$(basename "${sqsh_name%.*}")"
rm -f "${sqsh_name}"

if enroot import -o "${sqsh_name}" "docker://${image}"; then
    enroot create "${sqsh_name}"
else
    echo "[ERROR] Failed squash file \"${sqsh_name}\" for image \"${image}\"."
    exit 1
fi
