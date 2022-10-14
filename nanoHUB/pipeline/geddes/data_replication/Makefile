CPUS=$(shell getconf _NPROCESSORS_ONLN)
other_flags=
MAKEFLAGS += -j$(CPUS)

database_name=
table_name=
column_names=
date_column=

object-path=
save_as=csv
skip_existing=
log-level = INFO
FIRST_YEAR := 2000
LAST_YEAR := 2022
YEARS = $(shell seq ${FIRST_YEAR} ${LAST_YEAR})
SEMS = $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-01-01),year-07-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-07-01),year-12-31)))

#MONTHS = $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-01-01),year-01-31)))
#MONTHS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-02-01),year-02-28)))
#MONTHS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-03-01),year-03-31)))
#MONTHS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-04-01),year-04-30)))
#MONTHS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-05-01),year-05-31)))
#MONTHS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-06-01),year-06-30)))
#MONTHS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-07-01),year-07-31)))
#MONTHS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-08-01),year-08-31)))
#MONTHS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-09-01),year-09-30)))
#MONTHS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-10-01),year-10-31)))
#MONTHS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-11-01),year-11-30)))
#MONTHS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-12-01),year-12-31)))

JOBS = $(addprefix job,${SEMS})


.PHONY: all ${JOBS}

all: ${JOBS} ; echo "$@ success"
${JOBS}: job%:
	@echo $*
	python3 single_call.py \
    	--date_probe_range $* \
    	--object_path $(object-path) \
    	--save_as $(save_as) \
    	--database_name $(database_name)\
    	--table_name $(table_name) \
    	--column_names $(column_names) \
    	--date_column $(date_column) \
    	--skip_existing $(skip_existing) \
    	$(other_flags)


#--cost_probe_range $* \s