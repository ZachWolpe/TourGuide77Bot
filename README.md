# TourGuide77Bot

AI powered, tour guide chatbot for Telegram.

![TourGuide77Bot](https://github.com/ZachWolpe/TourGuide77Bot/blob/main/assets/full-arch-1.png)


```
: 27 Sep 2024
: zach.wolpe@medibio.com.au
```

## Prerequisites

Get started by cloning the repository:

```bash
git clone https://github.com/ZachWolpe/TourGuide77Bot.git
```

Both configurations will require setting up the following APIs:

    - Telegram Bot API.
    - Google Gemini API.
    - Setting up the AWS CLI.

Once these are configured, proceed to the relevant section below.

Create a `.env` file in the root directory and add the following environment variables:

```bash
GEMINI_API_KEY=<YOUR_GOOGLE_GEMINI_API_KEY>
BOT_API_TOKEN=<YOUR_TELEGRAM_BOT_API_TOKEN>
BOT_USERNAME=<YOUR_TELEGRAM_BOT_USERNAME>
```

Once these are configured, proceed to the relevant section below.

-------------------------
# Getting Started

This project is configured to run:
    1. Locally
    2. On AWS Lambda (hosted as a AWS ECR/Docker image)


## 1. Local Setup


####  1. Install dependencies

(Optional) Create a conda/mamba environment from `build/python-runtime.yml`

```bash
conda env create -f build/python-runtime.yml
```

Activate the environment:

```bash
conda activate telegram-bot
```

Alternatively, install the required packages using pip:

```bash
pip install -r requirements.txt
```

#### 2. Run the bot

```bash
python lambda_function.py
```

Voila! The bot is now running locally & can be interacted with via Telegram.


## 2. AWS Lambda Setup

### 1. Build the Docker image

```
docker build --platform linux/amd64 -t <Local-Docker-Image-Name>:<Tag> .
```


### 2. Create the ECR repository

```
aws ecr create-repository --repository-name <Local-Docker-Image-Name> --region your-region
```



### 3. Tag the Docker image

```
docker tag <Local-Docker-Image-Name>:<Tag> your-aws-account-id.dkr.ecr.your-region.amazonaws.com/<Image-name-on-ECR>:<Tag>
```


### 4. Authenticate Docker on the ECR registry

```
aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-account-id.dkr.ecr.your-region.amazonaws.com
```


### 5. Push the Docker image to ECR

```
docker push your-account-id.dkr.ecr.your-region.amazonaws.com/<Image-name-on-ECR>:<Tag>
```

### 6. Create the Lambda function

```
aws lambda create-function 
    --function-name <AWS-Lambda-function-name> \
    --package-type Image \
    --code ImageUri=your-account-id.dkr.ecr.your-region.amazonaws.com/<Image-name-on-ECR>:<Tag> \
    --role your-role-arn \
    --region your-region
```


### Note: Generate Temporary Credentials

Note: you may need to generate temporary credientials to authenticate with AWS CLI.

```
aws ecr get-login-password --region region | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com
```


### Rerun All (For Iterative Development)

Create temporary credentials:

```bash
aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-account-id.dkr.ecr.your-region.amazonaws.com
```

Once you have configured the build, you may want to rerun everything during development.

```bash
aws ecr get-login-password --region region | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com \ 
docker build -f build/dockerfile -t <> .
docker tag <Local-Docker-Image-Name>:<Tag> aws_account_id.dkr.ecr.us-west-2.amazonaws.com/<Image-name-on-ECR>:<Tag>
docker push aws_account_id.dkr.ecr.us-west-2.amazonaws.com/<Image-name-on-ECR>:<Tag>
aws lambda update-function-code --function-name <AWS-Lambda-function-name> --image-uri aws_account_id.dkr.ecr.us-west-2.amazonaws.com/<Image-name-on-ECR>:<Tag> --region your-region
```


------------------------
# Create a Webhook API Endpoint using AWS Gateway (Optional)

You may want you bot to be live, without needing to run a server to constantly poll Telegram for updates.

To achieve this, you can create a webhook API Gateway using AWS Management Console.


Follow these steps to create a Webhook API and connect it to your Lambda function:

1. Go to the AWS Management Console and navigate to API Gateway.

2. Click "Create API" and choose "HTTP API".

3. Under "Integrations", select "Add integration" and choose:
   - Integration type: Lambda
   - Lambda function: Select your Lambda function (telegram-bot-lambda)

4. Under "Configure routes":
   - Method: POST
   - Resource path: `/telegram`
   - Click "Next"

5. Review and create:
   - API name: TelegramBotWebhookAPI (or your preferred name)
   - Click "Create"

6. After creation, go to the "Stages" section:
   - You should see a default stage (often named $default)
   - Note the "Invoke URL" - this is your API endpoint

7. Go to your Lambda function in the AWS Lambda console:
   - Under "Configuration", click on "Permissions"
   - Scroll down to "Resource-based policy"
   - You should see a policy allowing API Gateway to invoke your function

### API Gateway URL

You should now have an endpoint route that looks like this:

```
https://<api-id>.execute-api.<region>.amazonaws.com/<stage>/telegram
```

Deploy the API and set the webhook URL in the Telegram Bot API.

### Set the Webhook URL

Set the webhook URL to the API Gateway URL:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<api-id>.execute-api.<region>.amazonaws.com/<stage>/telegram"
```

#### Delete the Webhook URL (Optional)

If you want to delete the webhook URL, you can do so with the following command:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"
```

------------------------------------
# API Safety - API Rate Limiting

Ensure to keep your keys secret and never commit them to a public repository.

Project your API Gateway from spam/bots/DDoS attacks by implementing a rate limit.

### A. Rate Limits for REST APIs

**Setting up Usage Plans and API Keys**

**Only Applicable for REST APIs**

```
1. REST APIs
   - Support Usage Plans and API Keys
   - More feature-rich, but can be more complex

2. HTTP APIs
   - Simpler and can be more cost-effective
   - Do not support Usage Plans and API Keys
   - Designed for low-latency, cost-effective integrations
```


1. In the API Gateway console, go to "Usage Plans".
2. Create a new usage plan with desired limits:
   - Rate limit (requests per second)
   - Burst limit (maximum concurrent requests)
   - Quota (requests per day/week/month)
3. Create an API key and associate it with the usage plan.
4. Require API key for your API method.


After creating a plan attach it to a stage:

```bash
aws apigateway create-usage-plan-key \
--usage-plan-id <usage-plan-id> \
--key-id <api-key-id> \
--key-type API_KEY
aws apigateway update-usage-plan \
--usage-plan-id <usage-plan-id> \
--patch-operations op='add',path='/apiStages',value='<api-id>:<stage-name>'
```


### B. Rate Limits for Lambda

Set up rate limits for your Lambda function to avoid unexpected costs.

Implement rate limiting in your Lambda function
    - Track request rates in `DynamoDB`
    - Implement your own rate limiting logic (in the Lambda function).

1. Create `dynamoDB` table to track request rates.


```bash
aws dynamodb create-table \
    --table-name <TABLE-NAME> \
    --attribute-definitions AttributeName=user_id,AttributeType=S \
    --key-schema AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```


Update your lambda function's enviroment variables to include the DynamoDB table name.


```bash
aws lambda update-function-configuration \
    --function-name <YOUR-LAMBDA-FUNCTION> \
    --environment "Variables={RATE_LIMIT_TABLE=<TABEL-NAME>}"
```


Update your Lambda function's IAM role to include DynamoDB permissions. 

Navigate to the IAM console and attach the following policy to the Lambda function's role.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:UpdateItem",
                "dynamodb:GetItem"
            ],
            "Resource": "arn:aws:dynamodb:YOUR_REGION:YOUR_ACCOUNT_ID:table/<TABEL-NAME>"
        }
    ]
}
```


----
Useful CLI commands:

View DynamoDB table to ensure the table was created successfully.

```bash
aws dynamodb scan --table-name <DynamDB-Table> --max-items 10
```



------------------------------
# Additional Resources

- [Telegram Bot API Tutorial](https://www.youtube.com/watch?v=vZtm1wuA2yc)
- [Telegram Webhook to AWS API Gateway](https://www.youtube.com/watch?v=oYMgw4M4cD0&t=885s)
