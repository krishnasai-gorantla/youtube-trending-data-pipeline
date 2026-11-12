# AWS Lambda source

The inspected AWS account contains one active function:

- Function: `de-youtube-raw-useast1-lambda-json-sheet`
- Runtime: Python 3.12
- Handler: `index.lambda_handler`
- Purpose inferred from its name and environment variable keys: JSON/reference-data transformation and Glue/S3 integration.

The deployment package has not yet been captured and reviewed, so the function's exact implementation and write behaviour are not documented here. Do not infer its input/output contract from environment variable names alone.

Before adding source code to this repository:

1. Export the deployment package from the Lambda console or retrieve it through an authorized, short-lived code URL.
2. Review it for embedded credentials, account-specific secrets and hard-coded resource names.
3. Replace secrets with environment variables / Secrets Manager references as appropriate.
4. Add a sanitized source version and document its trigger, input, output, dependencies and idempotency behaviour.
