---
name: aws-patterns
description: AWS architecture patterns, services, and best practices. Covers EKS, Lambda, CloudFormation, IAM, VPC, and AWS-specific solutions for production-grade cloud infrastructure.
---

# AWS Patterns

AWS architecture patterns and best practices across the AWS ecosystem, Well-Architected Framework, and cloud-native patterns.

## Workflow

1. **Design**: Apply Well-Architected pillars; select services based on workload characteristics
2. **Implement**: Use CDK/CloudFormation for IaC; configure VPC segmentation and IAM least privilege
3. **Secure**: Enable encryption, WAF, GuardDuty, Security Hub from day one
4. **Operate**: Monitor with CloudWatch/X-Ray, analyze costs, automate backup and DR

## Key Principles

1. **Managed services first**: Leverage AWS managed services for operational simplicity
2. **Security by design**: IAM least privilege, encryption at rest and in transit, defense in depth
3. **Multi-AZ by default**: Design for HA across availability zones from the start
4. **Infrastructure as code**: Everything in CloudFormation or CDK; no console-only changes
5. **Cost awareness**: Tag resources, set budgets, review Savings Plans and spot options
6. **Serverless when possible**: Lambda and Fargate for variable workloads

## Patterns

### EKS Cluster with IRSA

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  cluster_name    = "prod-eks"
  cluster_version = "1.29"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = false
  eks_managed_node_groups = {
    main = { instance_types = ["m6i.large"]; min_size = 2; max_size = 10 }
  }
}

module "irsa_s3" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name = "app-s3-reader"
  attach_s3_read_policy = true
  oidc_providers = {
    main = { provider_arn = module.eks.oidc_provider_arn; namespace_service_accounts = ["production:app-service"] }
  }
}
```

### IAM Least-Privilege with Conditions

```json
{
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": ["arn:aws:s3:::my-app-bucket", "arn:aws:s3:::my-app-bucket/*"],
    "Condition": { "StringEquals": { "aws:RequestedRegion": "eu-west-1" } }
  }]
}
```
