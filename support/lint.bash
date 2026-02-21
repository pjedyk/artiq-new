#! /usr/bin/env bash

set -eu -o pipefail -- "${@}" || exit
[[ "${#}" -eq 0 ]] || declare -- "${@}"

# NOTE: ARTIQ_TOP is set in envsetup.sh.
# shellcheck disable=SC2154
cd -- "${ARTIQ_TOP}"
printf -- '# %s=%q\n' ARTIQ_TOP "${PWD}"

_CMD="" _ALL=() _FAILED=()
_FILES_GIT="$( git ls-files -co --exclude-standard -- )"
mapfile -t -- _FILES <<<"${_FILES_GIT}"

_run() {
    printf -v _CMD -- ' %q' "${@}"
    printf -- '#%s\n' "${_CMD}"
    _ALL+=("${_CMD}")
    "${@}" || _failed "${@}"
}

_failed() {
    printf -- '%.0s^' {1..80}
    printf -- '\n'
    _FAILED+=("${_CMD}")
}

for _FILE in "${_FILES[@]}" ; do
    [[ -f "${_FILE}" ]] || continue --
    _FILE_REL="./${_FILE}"
    _FILE_DIR="${_FILE_REL%/*}"
    _FILE_NAME="${_FILE_REL##*/}"
    case "${_FILE_NAME}" in
        *.nix)
            _run alejandra -cq -- "${_FILE}"
        ;;
        *.bash|*.sh|.envrc)
            _run shellcheck -- "${_FILE}"
        ;;
        *.py)
            _run isort -c -- "${_FILE}"
            _run black -q --check --diff -- "${_FILE}"
            _run mypy -- "${_FILE}"
            _run pylint -sn -- "${_FILE}"
        ;;
        *)
        ;;
    esac
done

printf -- '\n'
printf -- '%.0s#' {1..80}
printf -- '\n'

if [[ "${#_FAILED[@]}" -ne 0 ]] ; then
    printf -- '\n# FAILED %d/%d\n' "${#_FAILED[@]}" "${#_ALL[@]}"
    printf -- '#  ⮑ %s\n' "${_FAILED[@]}"
fi

[[ "${#_FAILED[@]}" -eq 0 ]]
