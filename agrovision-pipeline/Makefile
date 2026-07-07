# Orchestrates execution commands for pipelines
.PHONY: init run status clean

init:
	@echo "Initializing DVC storage..."
	pip install -r requirements.txt
	dvc init
	# Configure local drive or cloud S3 as remote data store
	dvc remote add -d myremote /tmp/dvc-storage

run:
	@echo "Executing pipeline stages..."
	dvc repro

status:
	@echo "Comparing pipeline modifications..."
	dvc status

clean:
	@echo "Resetting pipeline directories..."
	rm -rf data/intermediate data/processed
	dvc gc -f
