"""
This module provide functions that wrap the function of the AWS Python SDK for SQS
"""
import os
import boto3 as boto3
from botocore.exceptions import ClientError


class SqsHandlerException(Exception):
    pass


def push_on_queue(message, queue):
    try:
        sqs = boto3.resource('sqs', region_name=os.getenv('AWS_REGION', 'eu-central-1'))
        queue = sqs.get_queue_by_name(QueueName=queue)
        response = queue.send_message(MessageBody=message, MessageGroupId='notificationGroup')
    except ClientError:
        raise SqsHandlerException()
