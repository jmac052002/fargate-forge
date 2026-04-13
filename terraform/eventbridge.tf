resource "aws_cloudwatch_event_rule" "intelligence" {
  name        = "${var.project_name}-intelligence-rule"
  description = "Trigger intelligence Lambda on CloudWatch alarm state change"

  event_pattern = jsonencode({
    source      = ["aws.cloudwatch"]
    detail-type = ["CloudWatch Alarm State Change"]
    detail = {
      state = {
        value = ["ALARM"]
      }
    }
  })

  tags = {
    Name = "${var.project_name}-intelligence-rule"
  }
} 

resource "aws_cloudwatch_event_target" "intelligence" {
  rule      = aws_cloudwatch_event_rule.intelligence.name
  target_id = "IntelligenceLambda"
  arn       = aws_lambda_function.intelligence.arn
}