I := .
O := build

override I := $(abspath $(I))
override O := $(abspath $(O))

CONFIG := debug

.PHONY: all
all:

$(O):
	mkdir -- "$(@)"

THIS = $(patsubst %/,%,$(dir $(lastword $(MAKEFILE_LIST))))

include $(wildcard */build.mk)
