terraform {
  backend "s3" {
    bucket       = "statefile-snowflake"
    key          = "dev/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = var.aws_region
}

resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  bucket_name = "${var.project_name}-${var.environment}-${random_id.suffix.hex}"

  csv_files = fileset("${path.module}/../data", "*.csv")

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "public-github-data-warehouse-demo"
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket" "raw_data" {
  bucket        = local.bucket_name
  force_destroy = var.force_destroy_bucket

  tags = merge(local.common_tags, {
    Name = local.bucket_name
  })
}

resource "aws_s3_bucket_public_access_block" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

data "aws_iam_policy_document" "allow_existing_role_read" {
  count = var.existing_s3_access_role_arn == "" ? 0 : 1

  statement {
    sid    = "AllowExistingRoleListRawPrefix"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = [var.existing_s3_access_role_arn]
    }

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.raw_data.arn
    ]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"

      values = [
        "${var.raw_data_prefix}/*"
      ]
    }
  }

  statement {
    sid    = "AllowExistingRoleReadRawObjects"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = [var.existing_s3_access_role_arn]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.raw_data.arn}/${var.raw_data_prefix}/*"
    ]
  }
}

resource "aws_s3_bucket_policy" "allow_existing_role_read" {
  count = var.existing_s3_access_role_arn == "" ? 0 : 1

  bucket = aws_s3_bucket.raw_data.id
  policy = data.aws_iam_policy_document.allow_existing_role_read[0].json

  depends_on = [
    aws_s3_bucket_public_access_block.raw_data
  ]
}

resource "aws_s3_object" "sample_csv_files" {
  for_each = local.csv_files

  bucket       = aws_s3_bucket.raw_data.id
  key          = "${var.raw_data_prefix}/${each.value}"
  source       = "${path.module}/../data/${each.value}"
  content_type = "text/csv"
  etag         = filemd5("${path.module}/../data/${each.value}")

  tags = local.common_tags
}
