#! /bin/false --

_IFS="${IFS}" IFS=:
_OFS="${OFS}" OFS=:

_PYTHONPATH=(
    "${PWD}/migen"
    ${PYTHONPATH}
)
export -- PYTHONPATH="${_PYTHONPATH[*]}"
unset -- _PYTHONPATH

IFS="${_IFS}"
OFS="${_OFS}"
unset -- _IFS _OFS
