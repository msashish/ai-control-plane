.PHONY: run-ollama

run-ollama:
	@echo "Starting Ollama server on port 8081..."
	@OLLAMA_HOST="127.0.0.1:8081" ollama serve & \
	SERVER_PID=$$! ; \
	echo "Waiting for Ollama to initialize..." ; \
	sleep 3 ; \
	echo "Registering model 'my-qwen' via Modelfile..." ; \
	OLLAMA_HOST="127.0.0.1:8081" ollama create my-qwen -f ./Modelfile ; \
	echo "Model registered successfully! Keeping server alive..." ; \
	wait $$SERVER_PID
