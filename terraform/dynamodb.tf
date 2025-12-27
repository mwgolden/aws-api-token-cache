resource "aws_dynamodb_table" "config_table" {
  name = "api_bot_config"
  billing_mode = "PROVISIONED"
  read_capacity = 1
  write_capacity = 1
  hash_key = "bot_name"

  attribute {
    name = "bot_name"
    type = "S"
  }

}

resource "aws_dynamodb_table" "api_token_cache_table" {
  name = "api_token_cache"
  billing_mode = "PROVISIONED"
  read_capacity = 1
  write_capacity = 1
  hash_key = "bot_name"
  range_key = "expires"

  attribute {
    name = "bot_name"
    type = "S"
  }

  attribute {
    name = "expires"
    type = "N"
  }

  ttl {
    attribute_name = "expires"
    enabled = true
  }
  
}