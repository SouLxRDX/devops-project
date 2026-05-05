terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-south-2"
}

# VPC
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "devops-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["ap-south-2a", "ap-south-2b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.3.0/24", "10.0.4.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  tags = {
    "kubernetes.io/cluster/devops-eks" = "shared"
  }

  public_subnet_tags = {
    "kubernetes.io/cluster/devops-eks" = "shared"
    "kubernetes.io/role/elb"           = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/devops-eks" = "shared"
    "kubernetes.io/role/internal-elb"  = "1"
  }
}

# EKS
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.0.0"

  cluster_name    = "devops-eks"
  cluster_version = "1.31"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access = true

  eks_managed_node_groups = {
  general = {
    desired_size = 2
    min_size     = 1
    max_size     = 2

    instance_types = ["t3.small"]
    capacity_type  = "SPOT"
  }
}

  tags = {
    Environment = "production"
    Project     = "devops-project"
  }
}