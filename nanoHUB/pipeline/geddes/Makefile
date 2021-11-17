other_flags=''

log-level = INFO

FIRST_YEAR := 2018
LAST_YEAR := 2021
YEARS = $(shell seq ${FIRST_YEAR} ${LAST_YEAR})

.PHONY: all ${YEARS}

all: ${YEARS} ; echo "$@ success"
${YEARS}: %:
	@echo $*
	python3 toolevents_by_semester.py \
		--year $* \
    	--bucket_name nanohub.raw \
    	--log_level $(log-level)