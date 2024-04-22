#!/usr/bin/env bash

apt update && apt install -y jq

pool_id=$(awslocal cognito-idp create-user-pool \
  --pool-name "$AWS_COGNITO_POOL"\
  --policies  '{"PasswordPolicy":{"MinimumLength":8,"RequireUppercase":false,"RequireLowercase":false,"RequireNumbers":false,"RequireSymbols":false}}' \
  --verification-message-template '{"DefaultEmailOption":"CONFIRM_WITH_LINK"}' \
  | jq -rc ".UserPool.Id")

echo "Pool created with id '$pool_id'"

client_id=$(awslocal cognito-idp create-user-pool-client \
  --user-pool-id "$pool_id" \
  --client-name "$AWS_COGNITO_POOL_CLIENT" \
  | jq -rc ".UserPoolClient.ClientId")

echo "Client created with id '$client_id'"

bucket_location=$(awslocal s3api create-bucket\
 --bucket "$AWS_S3_BUCKET" \
 | jq -rc ".Location")

echo "Bucket created with location '$bucket_location'"

queue_url=$(awslocal sqs create-queue --queue-name "$AWS_SQS_QUEUE"| jq -rc ".QueueUrl")

echo "Queue created with url '$queue_url'"