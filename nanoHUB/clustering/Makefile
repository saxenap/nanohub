CPUS=$(shell getconf _NPROCESSORS_ONLN)
other_flags=
#MAKEFLAGS += -j$(CPUS)

task = mike
bucket-name = nanohub.processed
object-path = clusters/${task-name}/by_semester
log-level = INFO
years = {2006..2021}
FIRST_YEAR := 2008
LAST_YEAR := 2021
YEARS = $(shell seq ${FIRST_YEAR} ${LAST_YEAR})
SEMS = $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-01-01),year-07-01)))
SEMS += $(foreach i,$(YEARS),$(subst year,$(i),$(join $(addsuffix _,year-07-02),year-12-31)))
JOBS = $(addprefix job,${SEMS})


.PHONY: all ${JOBS}

all: ${JOBS} ; echo "$@ success"
${JOBS}: job%:
	@echo $*
	python3 main_online_users_TS_analysis.py \
    	--cost_probe_range $* \
    	--class_probe_range $* \
    	--task $(task) \
    	--save_to_geddes \
    	--bucket_name $(bucket-name) \
    	--object_path $(object-path) \
    	--log_level $(log-level) \
    	$(other_flags)