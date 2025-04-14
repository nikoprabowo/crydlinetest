# Makefile for Terraform and DBT in Docker

TERRAFORM_CONTAINER=terraform
TERRAFORM_WORKDIR=/workspace
DBT_CONTAINER=dbt
DBT_WORKDIR=/workspace


# ---------- Terraform Commands ----------
tf-init:
	docker exec -it $(TERRAFORM_CONTAINER) terraform -chdir=$(TERRAFORM_WORKDIR) init

tf-fmt:
	docker exec -it $(TERRAFORM_CONTAINER) terraform -chdir=$(TERRAFORM_WORKDIR) fmt -recursive

tf-plan:
	docker exec -it $(TERRAFORM_CONTAINER) terraform -chdir=$(TERRAFORM_WORKDIR) plan

tf-apply:
	docker exec -it $(TERRAFORM_CONTAINER) terraform -chdir=$(TERRAFORM_WORKDIR) apply -auto-approve

tf-destroy:
	docker exec -it $(TERRAFORM_CONTAINER) terraform -chdir=$(TERRAFORM_WORKDIR) destroy -auto-approve

tf-validate:
	docker exec -it $(TERRAFORM_CONTAINER) terraform -chdir=$(TERRAFORM_WORKDIR) validate

tf-output:
	docker exec -it $(TERRAFORM_CONTAINER) terraform -chdir=$(TERRAFORM_WORKDIR) output

tf-shell:
	docker exec -it $(TERRAFORM_CONTAINER) sh


# ---------- DBT Commands ----------
dbt-debug:
	docker exec -it $(DBT_CONTAINER) dbt debug

dbt-run:
	docker exec -it $(DBT_CONTAINER) dbt run

dbt-test:
	docker exec -it $(DBT_CONTAINER) dbt test

dbt-clean:
	docker exec -it $(DBT_CONTAINER) dbt clean

dbt-docs:
	docker exec -it $(DBT_CONTAINER) dbt docs generate && docker exec -it $(DBT_CONTAINER) dbt docs serve

dbt-shell:
	docker exec -it $(DBT_CONTAINER) bash


# ---------- Ingest Raw Data Commands ----------
ingest-indicator:
	docker exec -it $(DBT_CONTAINER) python3 /app/ingest/ingest_indicator.py

ingest-coin:
	docker exec -it $(DBT_CONTAINER) python3 /app/ingest/ingest_coin.py

ingest-all: ingest-indicator ingest-coin