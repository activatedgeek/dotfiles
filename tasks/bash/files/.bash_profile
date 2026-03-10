# shellcheck disable=SC2148
if [ -f "${HOME}/.bashrc" ]; then
  # shellcheck disable=SC1091
  source "${HOME}/.bashrc"
fi

# shellcheck disable=SC2155
export __src_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for env_file in "${__src_dir}"/.*_env; do
    [ -f "${env_file}" ] || continue

    # shellcheck disable=SC1090
    source "${env_file}"
done

## Dynamic Profiles.

### brew.
if [[ -f /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"

    if [[ -f "$(brew --prefix)"/etc/bash_completion ]]; then
        # shellcheck disable=SC1091
        source "$(brew --prefix)"/etc/bash_completion
    fi
fi

### starship.
if [[ -x "$(command -v starship)" ]]; then
    if [[ "$TERM" != "dumb" ]]; then
        eval "$(starship init bash)"
    fi
fi

for profile_file in "${__src_dir}"/.*_profile; do
    [[ (-f "${profile_file}") && ("${profile_file}" != "${BASH_SOURCE[0]}") ]] || continue

    # shellcheck disable=SC1090
    source "${profile_file}"
done

for aliases_file in "${__src_dir}"/.*_aliases; do
    [ -f "${aliases_file}" ] || continue

    # shellcheck disable=SC1090
    source "${aliases_file}"
done

unset __src_dir
