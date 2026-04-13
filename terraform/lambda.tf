resource "aws_iam_role" "lambda_intelligence" {
  name = "${var.project_name}-lambda-intelligence"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-lambda-intelligence"
  }
} 

resource "aws_iam_role_policy_attachment" "lambda_intelligence" {
  role       = aws_iam_role.lambda_intelligence.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
} 

resource "aws_iam_role_policy" "lambda_intelligence" {
  name = "${var.project_name}-lambda-intelligence-policy"
  role = aws_iam_role.lambda_intelligence.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:DescribeAlarms"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "wafv2:GetIPSet",
          "wafv2:UpdateIPSet"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.alerts.arn
      }
    ]
  })
} 

resource "aws_lambda_function" "intelligence" {
  filename         = "${path.module}/../lambda/intelligence/function.zip"
  function_name    = "${var.project_name}-intelligence"
  role             = aws_iam_role.lambda_intelligence.arn
  handler          = "handler.handler"
  runtime          = "python3.12"
  timeout          = 60
  memory_size      = 256

  source_code_hash = filebase64sha256("${path.module}/../lambda/intelligence/function.zip")

  environment {
    variables = {
      BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
      SNS_TOPIC_ARN    = aws_sns_topic.alerts.arn
      ECS_CLUSTER      = aws_ecs_cluster.main.name
      ECS_SERVICE      = aws_ecs_service.app.name
      
    }
  }

  tags = {
    Name = "${var.project_name}-intelligence"
  }
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.intelligence.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.intelligence.arn
} 