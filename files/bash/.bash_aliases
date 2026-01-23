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

alias watch='watch '

if [ -f "${STORE_HOME}/uv/.venv/bin/dvc" ]; then
  alias dvc="${STORE_HOME}/uv/.venv/bin/dvc"
fi

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
alias rcp='rclone -P copy'
alias rcs='rclone -P sync'

## ruff.
alias ruffmt='uv run --no-sync ruff format'
alias ruffck='uv run --no-sync ruff check'
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
function uvr {
    ## Assumes .venv in the root of the git repo (handles submodules).
    if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        _git_root="$(git rev-parse --show-superproject-working-tree)"
        _uv_args="--no-project"
        if [[ -z "${_git_root}" ]]; then
            _git_root="$(git rev-parse --show-toplevel)"
            _uv_args="--no-sync"
        fi
    fi

    if [[ -n "${_git_root}" ]]; then
        _uv_args="${_uv_args} -p ${_git_root}/.venv/bin/python"
    fi
    unset _git_root

    uv run ${_uv_args} "${@}"
}
