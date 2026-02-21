#! /usr/bin/env bash

set -eu || exit

_CMD=(bash -l --)
[[ "${#}" -eq 0 ]] || _CMD=("${@}")

# shellcheck disable=SC2154
exec -- env -i -- HOME="${HOME}" TERM="${TERM}" SETUPSDK="${SETUPSDK}" DIRENV_DISABLE=1 \
    bash -cl -- "source -- \"\${SETUPSDK}\" && exec -- \"\${@}\"" yoctoshell "${_CMD[@]}"
