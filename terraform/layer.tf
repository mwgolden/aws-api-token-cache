data "archive_file" "api_token_cache" {
  type = "zip"
  source_dir = "../src"
  output_path = "../build/api_token_cache.zip"
}

resource "aws_lambda_layer_version" "api_token_cache_layer" {
  filename = data.archive_file.api_token_cache.output_path
  layer_name = "layer_api_token_cache"
  source_code_hash = data.archive_file.api_token_cache.output_base64sha256
}