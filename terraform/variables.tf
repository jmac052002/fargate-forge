variable "aws_region" {
  description = "The AWS region to deploy all resources."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "The name of the project, used for naming resources."
  type        = string
  default     = "fargate-forge"
}

variable "environment" {
  description = "Deploy environment (e.g., dev, staging, prod)."
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets."
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "availability_zones" {
  description = "List of availability zones to use for subnets."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "app_port" {
  description = "The port on which the FastAPI container listens on."
  type        = number
  default     = 8080
}

variable "app_image_tag" {
  description = "ECR image tag to deploy."
  type        = string
  default     = "latest"
}

variable "task_cpu" {
  description = "Fargate task CPU units (1024 = 1 vCPU)"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Fargate task memory in MB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 2
}

variable "github_repo" {
  description = "GitHub repo in owner/repo format"
  type        = string
  default     = "jmac052002/fargate-forge"
}

variable "github_branch" {
  description = "GitHub branch CodePipeline watches"
  type        = string
  default     = "main"
} 

variable "alert_email" {
  description = "Email address to receive infrastructure alerts"
  type        = string
} 
