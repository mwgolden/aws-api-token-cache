terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
  backend "s3" {
    bucket = "com.wgolden.tfstate"
    key    = "api-token-cache-lambda-layer/tfstate"
    region = "use-east-1"
  }
}