---
name: terraform-project-structure
description: Standard directory structure and patterns for Terraform projects
---

# Terraform Project Structure

When creating or reviewing Terraform projects, follow this standard structure.

## Standard Layout

```
tf-{project-name}/
├── global/                     # Main Terraform configuration
│   ├── {resource-type}.tf      # Resource definitions by type
│   ├── data.tf                 # Data sources
│   ├── outputs.tf              # Output definitions
│   ├── providers.tf            # Provider configuration
│   └── variables.tf            # Variable definitions
├── monitoring/                 # Monitoring infrastructure (optional)
│   ├── tfvars/
│   ├── monitoring.tf
│   └── monitoring_bootstrap.tf
├── tfvars/                     # Environment-specific variables
│   ├── development/
│   │   └── terraform.tfvars
│   ├── staging/
│   │   └── terraform.tfvars
│   └── production/
│       └── terraform.tfvars
├── scripts/                    # Helper scripts (optional)
├── docs/                       # Documentation (optional)
├── AGENTS.md                   # AI agent instructions
├── CONTRIBUTING.md             # Contribution guidelines
├── README.md                   # Project overview
├── justfile                    # Task runner commands
└── pipelines.yaml              # CI/CD pipeline config
```

## File Organization

### global/ directory

Organize `.tf` files by resource type or logical grouping:

- `providers.tf`: Provider configuration and versions
- `variables.tf`: Input variable definitions
- `outputs.tf`: Output value definitions
- `data.tf`: Data source lookups
- `{resource-type}.tf`: Resources grouped by type

### Example providers.tf
```hcl
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "terraform-state"
    key    = "project/terraform.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = var.aws_region
}
```

### Example variables.tf
```hcl
variable "environment" {
  description = "Deployment environment"
  type        = string
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-west-2"
}
```

## Naming Conventions

### Files
- Use lowercase with hyphens: `iam-roles.tf`
- Group related resources: `s3-buckets.tf`
- Use descriptive names: `workflow_slack_create_channel.tf`

### Resources
```hcl
# Use underscores in resource names
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project}-lambda-role-${var.environment}"
}

# Include purpose in name
resource "aws_s3_bucket" "data_lake_raw" {
  bucket = "${var.project}-data-lake-raw-${var.environment}"
}
```

### Variables
```hcl
# Use snake_case
variable "database_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}
```

## justfile Commands

```just
default:
    @just --list

# Format Terraform files
format:
    terraform fmt -recursive

# Validate configuration
validate:
    terraform init -backend=false
    terraform validate

# Lint with tflint
lint:
    tflint --recursive

# Security scan
security:
    tfsec .

# Plan for environment
plan env:
    cd global && terraform plan -var-file="../tfvars/{{env}}/terraform.tfvars"

# Apply for environment
apply env:
    cd global && terraform apply -var-file="../tfvars/{{env}}/terraform.tfvars"
```

## Best Practices

### 1. Use Variables for All Environment-Specific Values
```hcl
# Good
resource "aws_instance" "web" {
  instance_type = var.instance_type
  tags = {
    Environment = var.environment
  }
}

# Bad - hardcoded values
resource "aws_instance" "web" {
  instance_type = "t3.micro"
  tags = {
    Environment = "production"
  }
}
```

### 2. Add Descriptions to All Variables
```hcl
variable "retention_days" {
  description = "Number of days to retain logs before deletion"
  type        = number
  default     = 30
}
```

### 3. Use Locals for Computed Values
```hcl
locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket" "data" {
  bucket = "${var.project}-data-${var.environment}"
  tags   = local.common_tags
}
```

### 4. Use Data Sources for Existing Resources
```hcl
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "aws_iam_role" "lambda" {
  name = "lambda-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}
```

## Verification Checklist

- [ ] `providers.tf` has required_version and required_providers
- [ ] All variables have descriptions
- [ ] Environment-specific values use variables
- [ ] Resources use consistent naming (snake_case)
- [ ] `tfvars/` has directories for each environment
- [ ] `justfile` has format, validate, lint, plan, apply commands
- [ ] `README.md` documents the infrastructure
