CPUS=$(shell getconf _NPROCESSORS_ONLN)
other_flags=

log-level = INFO
#years = {2006..2021}
FIRST_YEAR := 2001
LAST_YEAR := 2015
YEARS = $(shell seq ${FIRST_YEAR} ${LAST_YEAR})
SEMS = $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-01-01),year-07-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-07-02),year-12-31)))
JOBS = $(addprefix job,${SEMS})


.PHONY: all ${JOBS}

all: ${JOBS} ; echo "$@ success"
${JOBS}: job%:
	@echo $*
	python3 overlap_by_semester.py \
    	--class_probe_range $* \
    	--log_level $(log-level) \
    	$(other_flags)
