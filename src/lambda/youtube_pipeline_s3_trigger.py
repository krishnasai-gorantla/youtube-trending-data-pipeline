import hashlib
import json
import logging
import os
from urllib.parse import unquote_plus

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
stepfunctions = boto3.client("stepfunctions")

EXPECTED_REGIONS = ("ca", "de", "fr", "gb", "in", "jp", "kr", "mx", "ru", "us")


def lambda_handler(event, context):
    """Start the batch state machine only when an explicit READY marker arrives."""
    state_machine_arn = os.environ["STATE_MACHINE_ARN"]
    raw_bucket = os.environ["RAW_BUCKET"]
    raw_prefix = os.environ.get(
        "RAW_PREFIX", "youtube/raw_statistics"
    ).strip("/")
    trigger_prefix = os.environ.get("TRIGGER_PREFIX", "pipeline_triggers/")

    started = []
    for record in event.get("Records", []):
        if record.get("eventSource") != "aws:s3":
            continue
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])
        if bucket != raw_bucket:
            logger.warning("Ignoring marker from unexpected bucket: %s", bucket)
            continue
        if not key.startswith(trigger_prefix) or not key.endswith(".ready"):
            logger.info("Ignoring non-marker object: %s", key)
            continue

        # Verify that the complete 10-region batch exists before starting ETL.
        missing = []
        for region in EXPECTED_REGIONS:
            source_key = f"{raw_prefix}/region={region}/{region.upper()}videos.csv"
            try:
                s3.head_object(Bucket=raw_bucket, Key=source_key)
            except ClientError as exc:
                if exc.response.get("Error", {}).get("Code") in (
                    "404", "NoSuchKey", "NotFound"
                ):
                    missing.append(source_key)
                else:
                    raise
        if missing:
            raise RuntimeError(
                "Batch-ready marker received, but raw CSV files are missing: "
                + ", ".join(missing)
            )

        sequencer = record["s3"]["object"].get("sequencer", "")
        marker_etag = record["s3"]["object"].get("eTag", "")
        identity = f"{bucket}/{key}:{sequencer}:{marker_etag}"
        execution_name = "youtube-" + hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()[:32]
        execution_input = {
            "trigger_bucket": bucket,
            "trigger_key": key,
            "marker_etag": marker_etag,
            "trigger_sequencer": sequencer,
        }

        try:
            response = stepfunctions.start_execution(
                stateMachineArn=state_machine_arn,
                name=execution_name,
                input=json.dumps(execution_input),
            )
            started.append({
                "executionArn": response["executionArn"],
                "executionName": execution_name,
            })
        except stepfunctions.exceptions.ExecutionAlreadyExists:
            logger.info(
                "Duplicate S3 notification ignored for execution %s",
                execution_name,
            )
            started.append({
                "executionName": execution_name,
                "duplicate": True,
            })

    logger.info("Pipeline trigger result: %s", json.dumps(started))
    return {"started": started, "records_received": len(event.get("Records", []))}
