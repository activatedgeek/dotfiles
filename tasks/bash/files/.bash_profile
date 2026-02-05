if [ -f "${HOME}/.bashrc" ]; then
  source "${HOME}/.bashrc"
fi

export __src_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for env_file in ${__src_dir}/.*_env; do
    [ -f "${env_file}" ] || continue
    
    source "${env_file}"
done

## Dynamic Profiles.

### brew.
if [[ -f /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"

    if [[ -f $(brew --prefix)/etc/bash_completion ]]; then
        . $(brew --prefix)/etc/bash_completion
    fi
fi

### starship.
if [[ -x "$(command -v starship)" ]]; then
    if [[ "$TERM" != "dumb" ]]; then
        eval "$(starship init bash)"
    fi
fi

for profile_file in ${__src_dir}/.*_profile; do
    [[ (-f "${profile_file}") && ("${profile_file}" != "${BASH_SOURCE[0]}") ]] || continue
    
    source "${profile_file}"
done

for aliases_file in ${__src_dir}/.*_aliases; do
    [ -f "${aliases_file}" ] || continue
    
    source "${aliases_file}"
done

unset __src_dir
