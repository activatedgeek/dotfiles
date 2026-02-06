## Common.
alias buba='brew upgrade && brew autoremove && brew cleanup -s'

alias dnsflush='sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder'

alias duh='du -h --max-depth=1 --threshold=1G . | sort -hr'

alias ls='ls --color=auto'

alias xargs='xargs '

alias watch='watch '

## docker.
alias cst='colima start'
alias cstop='colima stop'

alias drunit='docker run --rm -it'
alias drmi='docker rmi $(docker images | grep "^<none>" | awk "{print $3}")'
alias dprune='docker system prune'

alias dcup='docker compose up -d'
alias dcdown='docker compose down'
alias dcexec='docker compose exec'

## rclone.
alias rcp='rclone -P copy'
alias rcs='rclone -P sync'

## rsync.
alias rsync='rsync -avzhEP --stats'

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
