.PHONY: install run-local run-snowflake tf-init tf-plan tf-apply tf-destroy
install:
pip install -r requirements.txt

run-local:
streamlit run streamlit_app/app.py

run-snowflake:
APP_MODE=snowflake streamlit run streamlit_app/app.py

tf-init:
cd terraform && terraform init

tf-plan:
cd terraform && terraform fmt && terraform validate && terraform plan

tf-apply:
cd terraform && terraform apply

tf-destroy:
cd terraform && terraform destroy
