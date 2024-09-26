# TourGuide77Bot

AI powered, tour guide chatbot for Telegram.

![TourGuide77Bot](https://github.com/ZachWolpe/TourGuide77Bot/blob/main/assets/architecture.png)


```
: 26 Sep 2024
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


## Getting Started

This project is configured to run:
    1. Locally
    2. On AWS Lambda (hosted as a AWS ECR/Docker image)


-------------------------
### 1. Local Setup


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

-------------------------
### 2. AWS Lambda Setup

#### 1. Build the Docker image

```
docker build --platform linux/amd64 -t <Local-Docker-Image-Name>:<Tag> .
```


#### 2. Create the ECR repository

```
aws ecr create-repository --repository-name <Local-Docker-Image-Name> --region your-region
```


#### 3. Tag the Docker image

```
docker tag <Local-Docker-Image-Name>:<Tag> your-aws-account-id.dkr.ecr.your-region.amazonaws.com/<Image-name-on-ECR>:<Tag>
```

#### 4. Authenticate Docker on the ECR registry
```
aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-account-id.dkr.ecr.your-region.amazonaws.com
```


#### 5. Push the Docker image to ECR

```
docker push your-account-id.dkr.ecr.your-region.amazonaws.com/<Image-name-on-ECR>:<Tag>
```


#### 6. Create the Lambda function

```
aws lambda create-function 
    --function-name <AWS-Lambda-function-name> \
    --package-type Image \
    --code ImageUri=your-account-id.dkr.ecr.your-region.amazonaws.com/<Image-name-on-ECR>:<Tag> \
    --role your-role-arn \
    --region your-region
```



##### Note: Generate Temporary Credentials

Note: you may need to generate temporary credientials to authenticate with AWS CLI.

```
aws ecr get-login-password --region region | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com
```


aws ecr create-repository --repository-name lambda-telegram-bot --region your-region


#### 7. Rerun All (For Iterative Development)

Once you have configured the build, you may want to rerun everything during development.

```bash
docker build -t <> .
docker tag <Local-Docker-Image-Name>:<Tag> aws_account_id.dkr.ecr.us-west-2.amazonaws.com/<Image-name-on-ECR>:<Tag>
docker push aws_account_id.dkr.ecr.us-west-2.amazonaws.com/<Image-name-on-ECR>:<Tag>
aws lambda update-function-code --function-name <AWS-Lambda-function-name> --image-uri aws_account_id.dkr.ecr.us-west-2.amazonaws.com/<Image-name-on-ECR>:<Tag> --region your-region
```






----------
## Resources

- [Telegram Bot API Tutorial](https://www.youtube.com/watch?v=vZtm1wuA2yc)



