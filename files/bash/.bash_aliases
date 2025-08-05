## Misc.
alias buba='brew upgrade && brew autoremove && brew cleanup -s'

alias dnsflush='sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder'

alias duh='du -h --max-depth=1 --threshold=1G . | sort -hr'

alias ls='ls --color=auto'

alias mrun='micro run.sh && chmod +x run.sh && ./run.sh && rm run.sh'

alias nano=micro

alias oldrm='find . -mtime +2 -exec rm {} \;'

alias repip='pip install --no-cache-dir -UI'

alias xargs='xargs '

alias rsync='rsync -avzhEP --stats'

## docker.
alias cst='colima start'
alias cstop='colima stop'

alias drunit='docker run --rm -it'
alias drmi='docker rmi $(docker images | grep "^<none>" | awk "{print $3}")'
alias dprune='docker system prune'

alias dcup='docker compose up -d'
alias dcdown='docker compose down'
alias dcexec='docker compose exec'

## git.
alias gblack='git ls-files --other --modified --exclude-standard -- "*.py" "*.ipynb" | black'
function gdelhist {
  git checkout --orphan latest_branch
  git add -A
  git commit -am "[skip ci] init"
  git branch -D main
  git branch -m main
}

## rclone.
function rcpull() {
  rclone -P copy "${1}" "$(echo "${1}" | cut -d: -f2)"
}
function rcpush() {
  rclone -P copy "$(echo "${1}" | cut -d: -f2)" "${1}"
}

## ruff.
alias ruffmt='uv run ruff format'
alias ruffck='uv run ruff check'
alias gruffmt='git ls-files --other --modified --exclude-standard -- "*.py" | xargs ruffmt'
alias gruffck='git ls-files --other --modified --exclude-standard -- "*.py" | xargs ruffck'

## setfacl.
alias setfaclnogo='setfacl -m g::-,o::-'
alias setfaclrx='setfacl -m g::rx,o::rx'

## tmux.
alias ta='tmux attach -t'
alias tls='tmux ls'
alias tn='tmux new -s'

## torch/jax.
function ddprun {
  __nnodes=${NNODES:-1}
  __nproc_per_node=${NPROC_PER_NODE:-$(python -c "import torch; print(torch.cuda.device_count())")}
  __rdzv_id=${MPROC_GROUPID:-$(date +%s)}
  __host=${MPROC_HOST:-$(hostname)}
  __port=${MPROC_PORT:-$(python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()')}
  __rdzv_endpoint=${__host}:${__port}
  __node_rank=${MRANK:-0}

  torchrun \
      --rdzv-backend=c10d \
      --nnodes=${__nnodes} \
      --nproc_per_node=${__nproc_per_node} \
      --rdzv_id=${__rdzv_id} \
      --rdzv_endpoint=${__rdzv_endpoint} \
      --node_rank=${__node_rank} \
  "${@}"
}
function jaxrun {
  __nproc_per_node=${NPROC_PER_NODE:-$(python -c "import torch; print(torch.cuda.device_count())")}
  mpirun \
    -n ${__nproc_per_node} \
    python "${@}"
}

## micromamba.
function mmc {
  __venv_path=${VENV_DIR:-"${PROJECT_HOME}/$(basename "$(pwd)")"}/.venv
  if [[ ! -d "${__venv_path}" ]]; then
    micromamba create -y --prefix "${__venv_path}" -c conda-forge python=${PY_VERSION:-3.11} pip
  fi
  if [[ ! "$(pwd)" -ef "${PROJECT_HOME}/$(basename "$(pwd)")" ]]; then
    rm -rf .venv
    ln -sf "${__venv_path}" .venv
  fi
  unset __venv_path
}
alias mm='micromamba -p ./.venv'

## uv.
function uvc {
  __venv_path=${VENV_DIR:-"${PROJECT_HOME}/$(basename "$(pwd)")"}/.venv
  if [[ ! -d "${__venv_path}" ]]; then
    uv venv --python ${PY_VERSION:-3.11} ${__venv_path}
  fi
  if [[ ! "$(pwd)" -ef "${PROJECT_HOME}/$(basename "$(pwd)")" ]]; then
    rm -rf .venv
    ln -sf "${__venv_path}" .venv
  fi
  unset __venv_path
}
alias uvr='uv run --no-sync'
alias uvs='uv sync --no-install-project'
alias uvsa='uv sync --all-extras'
