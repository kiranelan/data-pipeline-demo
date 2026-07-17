Architecture:

CSV -> S3 -> Snowflake Stage -> Snowflake Views -> Streamlit Dashboard

Key files:

requirements.txt
----------------

Sample customers.csv
--------------------
customer_id,customer_name,country,segment,plan_type,signup_date,status
1001,Northstar Retail,USA,Enterprise,Premium,2024-01-15,Active
1002,BluePeak Logistics,USA,Business,Standard,2024-02-11,Active
...

Terraform creates:
- S3 Bucket
- Uploads sample CSV files
- Outputs Snowflake stage URL

Snowflake setup:
- Database: TELECOM_WAREHOUSE_DEMO
- Schemas: RAW, ANALYTICS
- Warehouse: TELECOM_DEMO_XS_WH
- Tables: CUSTOMERS, USAGE_RECORDS, BILLING, SUPPORT_TICKETS
- Views: VW_MONTHLY_REVENUE, VW_CUSTOMER_REVENUE, VW_USAGE_SUMMARY, VW_SUPPORT_METRICS, VW_EXECUTIVE_KPIS

Run locally:
```python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```


Deploy AWS:
```bash
cd terraform
terraform init
terraform apply
```
Run Snowflake mode:
APP_MODE=snowflake streamlit run streamlit_app/app.py
