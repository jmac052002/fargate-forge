resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts"

  tags = {
    Name = "${var.project_name}-alerts"
  }
} 

resource "aws_sns_topic_subscription" "alerts_email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
} 

output "sns_topic_arn" {
  description = "ARN of the alerts SNS topic"
  value       = aws_sns_topic.alerts.arn
}