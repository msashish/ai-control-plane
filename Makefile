SHELL := /bin/bash
MAKEFILE_NAME := $(lastword $(MAKEFILE_LIST))

ROOT_DIR := $(CURDIR)
RUN_DIR := $(ROOT_DIR)/.run
LOG_DIR := $(ROOT_DIR)/.log

LLM_PORT 			?= 8081
CLASSIFIER_PORT 	?= 8085
GATEWAY_PORT 		?= 4000
UI_PORT 			?= 5173
CLASSIFIER_RELOAD 	?= false

# Ollama settings
OLLAMA 					?= ollama
#OLLAMA_HOST_ADDR 		:= 127.0.0.1:${LLM_PORT}
OLLAMA_HOST_ADDR 		:= localhost:${LLM_PORT}
OLLAMA_MODEL_NAME 		?= my-qwen
LLM_MODEL				?= qwen-gguf
LLM_MODEL_DIR				?= ${ROOT_DIR}/local-llm/models
# generated at runtime
OLLAMA_MODELFILE		:= ${RUN_DIR}/Modelfile

LLM_HEALTH_URL 			:= http://${OLLAMA_HOST_ADDR}/api/version
CLASSIFIER_HEALTH_URL 	:= http://localhost:${CLASSIFIER_PORT}/health
GATEWAY_HEALTH_URL 		:= http://localhost:${GATEWAY_PORT}/health/liveliness

HEALTH_TIMEOUT 			?= 60
LLM_HEALTH_TIMEOUT 		?= 60
CURL_CONNECT_TIMEOUT 	?= 2
CURL_MAX_TIME 			?= 5

# Use LLMLite's local bundled cost map
# export LITELLM_LOCAL_MODEL_COST_MAP := True

# wait_for <name> <url> <timeout> <logfile>
define wait_for
	@printf "Waiting for %s at %s " "${1}" "${2}" ; \
	for i in $$(seq 1 ${3}) ; do \
		if curl -sf --connect-timeout ${CURL_CONNECT_TIMEOUT} --max-time ${CURL_MAX_TIME} -o /dev/null "${2}"  ; then \
			echo " ready" ; \
			exit 0 ; \
		fi ; \
		printf "." ; sleep 1; \
	done ; \
	echo " FAILED after ${3}s" ; \
	echo "--- last 30 lines of ${4} ---" ; \
	tail -n 30 "${4}" 2>/dev/null ; \
	exit 1
endef

# start_py <name> <dir> <url> <port>
define start_py
	@mkdir -p ${RUN_DIR} ${LOG_DIR} 
	@if [ -f $(RUN_DIR)/$(1).pid ] && kill -0 $$(cat $(RUN_DIR)/$(1).pid) 2>/dev/null; then \
		echo "Warning: ${1} is already running (pid $$(cat $(RUN_DIR)/$(1).pid))" ; \
	elif lsof -ti tcp:$(4) -sTCP:LISTEN >/dev/null 2>&1; then \
		echo "Error: Port $(4) is already in use. Please stop the process and try again." ; \
		exit 1 ; \
	else \
		echo "Starting ${1} on port $(4)..." ; \
		cd $(ROOT_DIR)/$(2) && { nohup env CLASSIFIER_RELOAD=$(CLASSIFIER_RELOAD) uv run python main.py > $(LOG_DIR)/$(1).log 2>&1 & echo $$! > ${RUN_DIR}/$(1).pid ; }; \
	fi
	$(call wait_for,${1},${3},${HEALTH_TIMEOUT},${LOG_DIR}/${1}.log)
endef

# stop_proc <name> : kills the whole process tree (e.g. uv -> python -> uvicorn workers,)
define stop_proc
	@if [ -f $(RUN_DIR)/$(1).pid ]; then \
		pid=$$(cat $(RUN_DIR)/$(1).pid) ; \
		kill_tree() { \
			children=$$(pgrep -P $$1) ; \
			for child in $$children; do \
				kill_tree $$child ; \
			done ; \
			kill $$1 2>/dev/null ; } ; \
		if kill -0 $$pid 2>/dev/null; then \
			echo "Stopping ${1} (pid $$pid)..." ; \
			kill_tree $$pid ; \
			for i in $$(seq 1 10); do \
				kill -0 $$pid 2>/dev/null || break ; \
				sleep 1 ; \
			done ; \
			kill -0 $$pid 2>/dev/null && kill -9 $$pid 2>/dev/null ; \
		else \
			echo "Warning: ${1} is not running (stale pid file)." ; \
		fi ; \
		rm -f $(RUN_DIR)/$(1).pid ; \
	else \
		echo "Warning: ${1} not running." ; \
	fi
endef

.PHONY: help up down restart test status logs logs-llm logs-classifier logs-gateway \
	llm llm-serve llm-model llm-recreate classifier gateway stop-llm stop-classifier stop-gateway 

help:
	@echo "Usage: make <target>"
	@echo "Targets:"
	@echo "  up                 Start llm (ollama) -> classifier -> gateway -> ui"
	@echo "  down               Stop all services"
	@echo "  restart            down + up"
	@echo "  test               Run ai-gateway/tests"
	@echo "  status             Show status of all services"
	@echo "  logs               Tail all logs (logs-llm | logs-classifier | logs-gateway | logs-ui)"
	@echo "  llm                Start "ollama serve" on port $(LLM_PORT) and register model '$(OLLAMA_MODEL_NAME)' via Modelfile"
	@echo "  llm-serve          Start LLM server only"
	@echo "  llm-model          Register LLM model only"
	@echo "  llm-recreate       Re-register model '$(OLLAMA_MODEL_NAME)' from Modelfile (requires LLM server to be running)"
	@echo "  classifier | gateway        						Start one service"
	@echo "  stop-llm  | stop-classifier | stop-gateway         Stop one service"

up: llm classifier gateway
	@echo ""
	@$(MAKE) --no-print-directory -f $(MAKEFILE_NAME) status

down: stop-gateway stop-classifier stop-llm
	@$(MAKE) --no-print-directory -f $(MAKEFILE_NAME) status

restart:
	@$(MAKE) --no-print-directory -f $(MAKEFILE_NAME) down
	@$(MAKE) --no-print-directory -f $(MAKEFILE_NAME) up

# --- local LLM (native ollama) ---	
llm: llm-serve llm-model

llm-serve:
	@command -v $(OLLAMA) >/dev/null 2>&1 || { echo "Error: '$(OLLAMA)' is not installed. Install with: brew install ollama."; exit 1; }
	@mkdir -p ${RUN_DIR} ${LOG_DIR}
	@if [ -f $(RUN_DIR)/llm.pid ] && kill -0 $$(cat $(RUN_DIR)/llm.pid) 2>/dev/null; then \
		echo "LLM inference is already running (pid $$(cat $(RUN_DIR)/llm.pid))" ; \
	elif lsof -ti tcp:$(LLM_PORT) -sTCP:LISTEN >/dev/null 2>&1; then \
		echo "Error: Port $(LLM_PORT) is already in use. Please stop the process and try again." ; \
		exit 1 ; \
	else \
		echo "Starting LLM (ollama serve) on $(OLLAMA_HOST_ADDR)..." ; \
		OLLAMA_HOST=$(OLLAMA_HOST_ADDR) nohup $(OLLAMA) serve > $(LOG_DIR)/llm.log 2>&1 & echo $$! > ${RUN_DIR}/llm.pid ; \
	fi
	$(call wait_for,LLM,$(LLM_HEALTH_URL),$(LLM_HEALTH_TIMEOUT),$(LOG_DIR)/llm.log)

llm-model:
	@if OLLAMA_HOST=$(OLLAMA_HOST_ADDR) $(OLLAMA) show $(OLLAMA_MODEL_NAME) >/dev/null 2>&1; then \
		echo "Model '$(OLLAMA_MODEL_NAME)' is already registered." ; \
	else \
		$(MAKE) --no-print-directory -f $(MAKEFILE_NAME) llm-recreate ; \
	fi

llm-recreate:
	@test -f $(LLM_MODEL_DIR)/$(LLM_MODEL) || { echo "Error: Modelfile '$(LLM_MODEL_DIR)/$(LLM_MODEL)' not found. Please create it first."; exit 1; }
	@mkdir -p ${RUN_DIR} 
	@echo "FROM $(LLM_MODEL_DIR)/$(LLM_MODEL)" > $(OLLAMA_MODELFILE)
	@echo "Registering model '$(OLLAMA_MODEL_NAME)' from $(LLM_MODEL_DIR)/$(LLM_MODEL)..."
	@OLLAMA_HOST=$(OLLAMA_HOST_ADDR) $(OLLAMA) create $(OLLAMA_MODEL_NAME) -f $(OLLAMA_MODELFILE)

stop-llm:
	$(call stop_proc,llm)

# ---- classifier ----
classifier:
	$(call start_py,classifier,classifier,$(CLASSIFIER_HEALTH_URL),$(CLASSIFIER_PORT))

stop-classifier:
	$(call stop_proc,classifier)

# ---- gateway ----
gateway:
	$(call start_py,gateway,ai-gateway,$(GATEWAY_HEALTH_URL),$(GATEWAY_PORT))

stop-gateway:
	$(call stop_proc,gateway)	

test:
	@echo "Running tests..."
	@curl -sf --connect-timeout ${CURL_CONNECT_TIMEOUT} --max-time ${CURL_MAX_TIME} -o /dev/null $(GATEWAY_HEALTH_URL) || { echo "Error: Gateway is not running. Run 'make up' first."; exit 1; }
	@cd ai-gateway && uv run python test.py

status:
	@check() { if curl -sf --connect-timeout ${CURL_CONNECT_TIMEOUT} --max-time ${CURL_MAX_TIME} -o /dev/null "$$2" ; then s="UP" ; else s="DOWN" ; fi ; printf "  %-11s %-5s %s\n" "$$1" "$$s" "$$2"; }; \
	echo "Service Status:" ; \
	check llm $(LLM_HEALTH_URL) ; \
	check classifier $(CLASSIFIER_HEALTH_URL) ; \
	check gateway $(GATEWAY_HEALTH_URL) ; \

logs: 
	@mkdir -p ${LOG_DIR}; touch ${LOG_DIR}/llm.log ${LOG_DIR}/classifier.log ${LOG_DIR}/gateway.log
	tail -n 50 -f ${LOG_DIR}/llm.log ${LOG_DIR}/classifier.log ${LOG_DIR}/gateway.log

logs-llm:
	tail -n 100 -f ${LOG_DIR}/llm.log

logs-classifier:
	tail -n 100 -f ${LOG_DIR}/classifier.log

logs-gateway:
	tail -n 100 -f ${LOG_DIR}/gateway.log