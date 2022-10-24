CPUS=$(shell getconf _NPROCESSORS_ONLN)
other_flags=
#MAKEFLAGS += -j$(CPUS)


chunk_size=100

log-level = INFO
FIRST_YEAR := 2001
LAST_YEAR := 2022
YEARS = $(shell seq ${FIRST_YEAR} ${LAST_YEAR})
SEMS = $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-01-01),year-02-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-02-01),year-03-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-03-01),year-04-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-04-01),year-05-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-05-01),year-06-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-06-01),year-07-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-07-01),year-08-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-08-01),year-09-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-09-01),year-10-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-10-01),year-11-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-11-01),year-12-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-12-01),year-12-31)))
JOBS = $(addprefix job,${SEMS})


.PHONY: all ${JOBS}

all: ${JOBS} ; echo "$@ success"
${JOBS}: job%:
	@echo $*
	python3 computed_needs.py \
    	--date_probe_range $* \
    	--chunk_size $(chunk_size) \
    	$(other_flags)


#--cost_probe_range $* \s