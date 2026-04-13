fargate-forge

A production-grade CI/CD and container platform on AWS, built as a portfolio project demonstrating real-world cloud engineering practices. Every component is provisioned with Terraform and deployed through a fully automated pipeline.

## Architecture
GitHub → CodePipeline → CodeBuild → ECR → CodeDeploy (Blue/Green) → ECS Fargate → ALB
↑
WAF + CloudWatch

## Stack

| Layer | Technology |
|---|---|
| Application | Python 3.11, FastAPI, pytest |
| Containerization | Docker, Amazon ECR |
| Orchestration | Amazon ECS Fargate |
| CI/CD | AWS CodePipeline, CodeBuild, CodeDeploy (Blue/Green) |
| Infrastructure as Code | Terraform |
| Networking | VPC, public/private subnets, ALB, Security Groups |
| Security | AWS WAF, Secrets Manager, IAM least-privilege roles |
| Observability | CloudWatch Container Insights, structured logging |

## Project Structure
```
fargate-forge/
├── app/                          # FastAPI application
│   ├── main.py                   # Application entrypoint
│   ├── requirements.txt
│   └── Dockerfile
├── lambda/
│   └── intelligence/             # Autonomous remediation Lambda
│       ├── handler.py            # Claude-powered intelligence engine
│       └── requirements.txt
├── tests/                        # pytest test suite
│   ├── conftest.py
│   └── test_api.py
├── terraform/                    # All infrastructure as code
│   ├── main.tf                   # Provider, data sources
│   ├── variables.tf
│   ├── vpc.tf                    # VPC, subnets, routing
│   ├── alb.tf                    # Application Load Balancer, target groups
│   ├── ecr.tf                    # Container registry
│   ├── ecs.tf                    # Cluster, task definition, service
│   ├── codebuild.tf              # Build project and IAM
│   ├── codedeploy.tf             # Blue/green deployment group
│   ├── codepipeline.tf           # Pipeline stages
│   ├── waf.tf                    # WAF WebACL
│   ├── cloudwatch.tf             # Container Insights, log groups, dashboard
│   ├── lambda.tf                 # Intelligence Lambda, IAM
│   ├── eventbridge.tf            # Alarm routing rule and target
│   └── sns.tf                    # Alert topic and subscription
├── buildspec.yml                 # CodeBuild pipeline definition
├── appspec.yaml                  # CodeDeploy ECS deployment spec
└── taskdef.json                  # ECS task definition template
```
## CI/CD Pipeline

Every push to `main` triggers a full pipeline run:

1. **Source** CodePipeline detects the GitHub commit via CodeConnections
2. **Build** CodeBuild runs pytest, builds a Docker image, tags it with the build number, and pushes to ECR. The task definition is generated dynamically from the live ECS state and the image URI is injected via `sed`
3. **Deploy** CodeDeploy performs a blue/green deployment to ECS Fargate. New tasks spin up on the green target group, pass ALB health checks, traffic shifts, and old tasks terminate after a 5-minute wait

## Autonomous Infrastructure Intelligence (Option C)

A self-healing layer built on AWS Lambda and Amazon Bedrock (Claude) that monitors, reasons, and remediates infrastructure events automatically.

**How it works:**
1. CloudWatch detects a threshold breach (e.g. ECS CPU > 80% for 10 minutes)
2. EventBridge routes the alarm event to a Lambda function
3. Lambda invokes Claude via Bedrock with full alarm context
4. Claude analyzes the event, identifies root cause, and recommends an action
5. Lambda executes the remediation (scale ECS tasks, block IPs in WAF, or monitor)
6. An incident report is published to SNS and delivered via email

**Design decisions:**
- Claude responds in structured JSON only making AI output deterministic and safe for automated execution
- Incremental scaling reads current task count before acting never assumes system state
- Defense-in-depth error handling SNS alert fires before Lambda re-raises, ensuring human notification even on failure
- Least-privilege IAM Bedrock permission scoped to exact model ARN, SNS publish scoped to exact topic ARN

## Infrastructure

All infrastructure is managed with Terraform. The VPC uses a standard multi-AZ design with public subnets for the ALB and private subnets for ECS tasks.

**Cost control**: Infrastructure is torn down between sessions with `terraform destroy` and rebuilt with `terraform apply`. The pipeline triggers automatically after each rebuild.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check — returns `{"status": "healthy"}` |
| GET | `/info` | Service info |

## Running Locally

```bash
cd app
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

```bash
pytest tests/ -v
```

## Deployment

```bash
# Provision infrastructure
cd terraform
terraform init
terraform apply

# Pipeline triggers automatically on git push
git push origin main
```

## Key Engineering Decisions

**Dynamic task definition generation** Rather than maintaining a static `taskdef.json` with a placeholder, the build fetches the live task definition from ECS, strips read-only fields, and injects the new image URI via `sed`. This sidesteps a known validation issue with CodeDeploy's `Image1ContainerName` substitution and produces a cleaner, more reliable artifact.

**Blue/green over rolling** CodeDeploy blue/green gives zero-downtime deployments with automatic rollback on health check failure. The ALB handles traffic shifting between target groups transparently.

**Terraform lifecycle management** The ECS service uses `ignore_changes = [task_definition, load_balancer]` so Terraform doesn't fight CodeDeploy over service state between deployments.

**Least-privilege IAM** Each service (CodeBuild, CodeDeploy, CodePipeline, ECS task execution) has its own scoped IAM role with only the permissions it needs.

## Author

Joseph McCoy transitioning into cloud/DevOps engineering. Building real projects on AWS to demonstrate production-ready skills.

[LinkedIn](www.linkedin.com/in/joseph-mccoy-68a5591b3) · [GitHub](https://github.com/jmac052002)
