OUTDIR-PATH := /out/papermill
CD-OUTDIR := cd /out/papermill/
OUTDIR-FULL-PATH := $(OUTDIR-PATH)/$(shell date +'%Y')/$(shell date +'%m')/$(shell date +'%d')

prepare-outdir:
	mkdir -p ${OUTDIR-FULL-PATH}
	$(CD-OUTDIR) && \
		git init && \
		git remote add origin $${GIT_OUTFILE_REMOTE_URL} && \
		git fetch origin && \
		git checkout -b production origin/production && \
		git pull --rebase origin production

execute-notebook: prepare-outdir
	papermill /app/$(name).ipynb ${OUTDIR-FULL-PATH}/$(name)-$(shell date +'%H-%M-%S').ipynb
	$(CD-OUTDIR) && \
		git add -A && \
		git commit -m "$(name)" && \
		#git push origin production && \
		echo 'FINISHED'\


