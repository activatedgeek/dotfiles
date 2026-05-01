#!/usr/bin/env bash

sed -i "s/^concurrent = .*/concurrent = ${GLOBAL_CONCURRENT:-4}/" /etc/gitlab-runner/config.toml
