OUTDIR-PATH := /out/papermill
CD-OUTDIR := cd /out/papermill/
OUTDIR-FULL-PATH := $(OUTDIR-PATH)/$(shell date +'%Y')/$(shell date +'%m')/$(shell date +'%d')

new-relic:
	newrelic-admin run-program python3 /app/notebook_executor.py

prepare-outdir:
	@mkdir -p ${OUTDIR-FULL-PATH}
	@$(CD-OUTDIR) && \
		git init && \
		git remote add origin $${GIT_OUTFILE_REMOTE_URL} && \
		git fetch origin && \
		git checkout -b production origin/production && \
		git pull --rebase origin production

execute-notebook: new-relic prepare-outdir
	papermill /app/$(name).ipynb ${OUTDIR-FULL-PATH}/$(name)-$(shell date +'%H-%M-%S').ipynb
	@$(CD-OUTDIR) && \
		git add -A && \
		git commit -m "$(name)" && \
		git push origin production