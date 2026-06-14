# shellcheck disable=SC2148
## Common.
alias buba='brew upgrade && brew autoremove && brew cleanup -s'

alias dnsflush='sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder'

alias duh='du -h --max-depth=1 --threshold=1G . | sort -hr'

alias ls='ls --color=auto'

alias xargs='xargs '

alias watch='watch '

alias fastrm='rsync -av --delete $(mktemp -d)/'

## docker.
alias cst='colima start'
alias cstop='colima stop'

## rclone.
alias rcp='rclone -P copy'
alias rcs='rclone -P sync'

## rsync.
alias rsync='rsync -avzhEP --stats'

## zellij
alias zl=zellij

## Misc.
function safe_echo {
    mask_vars=()
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--string)
                mask_str="${2}"
                shift 2
            ;;
            -m|--mask-variables)
                IFS=',' read -ra mask_vars <<< "${2}"
                shift 2
            ;;
            *)
                shift 1
            ;;
        esac
    done

    ## Also mask any other protected env vars.
    for env_row in $(env | grep -E 'TOKEN|API_KEY|PASSWORD'); do
        mask_vars+=("$(echo "${env_row}" | cut -d= -f1)")
    done

    for mask_var in "${mask_vars[@]}"; do
        mask_str="$(echo "$mask_str" | sed -e "s|\\\$${mask_var}|*******|g" -e "s|\\\$\\\{${mask_var}\\\}|*******|g" -e "s|${!mask_var}|*******|g")"
    done

    echo "${mask_str}"
    unset mask_vars mask_var mask_str
}
