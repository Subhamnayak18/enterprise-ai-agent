# Deployment approach

## Low-cost AWS path

For a portfolio deployment, run the FastAPI container on AWS App Runner (or ECS Fargate if more control is needed), Streamlit as a second container/service, and PostgreSQL on a small RDS PostgreSQL instance. Store API/database secrets in AWS Secrets Manager or Parameter Store. Chroma persistence can remain on attached storage for the demo; a real enterprise deployment would normally use a managed vector database or PostgreSQL/pgvector and durable object storage for documents.

The CI workflow tests and builds the image. Production deployment should use a dedicated IAM role, HTTPS, authentication, rate limiting, network restrictions, read-only SQL credentials for the agent, backups, monitoring and budget alerts.

Cost warning: RDS and always-on container services can incur charges. Tear down portfolio resources when not in use and configure billing alerts.
