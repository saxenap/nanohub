OUTDIR-PATH := /out/papermill
CD-OUTDIR := cd /out/papermill/
OUTDIR-FULL-PATH := $(OUTDIR-PATH)/$(shell date +'%Y')/$(shell date +'%m')/$(shell date +'%d')

prepare-outdir:
	mkdir -p ${OUTDIR-FULL-PATH}

execute-notebook: prepare-outdir
	python3 hello-world.py


