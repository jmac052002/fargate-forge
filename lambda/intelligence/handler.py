import json
import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client("bedrock-runtime", region_name=os.environ["AWS_REGION"])
ecs = boto3.client("ecs", region_name=os.environ["AWS_REGION"])
waf = boto3.client("wafv2", region_name=os.environ["AWS_REGION"])
sns = boto3.client("sns", region_name=os.environ["AWS_REGION"]) 

def handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract alarm details from EventBridge event
        detail = event.get("detail", {})
        alarm_name = detail.get("alarmName", "unknown")
        alarm_state = detail.get("state", {}).get("value", "unknown")
        reason = detail.get("state", {}).get("reason", "No reason provided")
        
        logger.info(f"Alarm: {alarm_name}, State: {alarm_state}, Reason: {reason}")
        
        # Build context for Claude
        prompt = f"""You are an AWS infrastructure intelligence system.
        
A CloudWatch alarm has triggered with the following details:
- Alarm Name: {alarm_name}
- State: {alarm_state}  
- Reason: {reason}

Analyze this event and respond with a JSON object containing:
1. "severity": "low", "medium", or "high"
2. "root_cause": your assessment of what caused this
3. "action": one of "scale_up", "scale_down", "block_ip", "rollback", or "monitor"
4. "explanation": a clear explanation of your reasoning

Respond only with valid JSON, no other text.""" 

        # Invoke Claude via Bedrock
        bedrock_response = bedrock.invoke_model(
            modelId=os.environ["BEDROCK_MODEL_ID"],
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        # Parse Claude's response
        response_body = json.loads(bedrock_response["body"].read())
        claude_response = json.loads(response_body["content"][0]["text"])
        
        logger.info(f"Claude analysis: {json.dumps(claude_response)}")
        
        # Execute remediation based on Claude's recommendation
        action = claude_response.get("action")
        severity = claude_response.get("severity")
        
        remediation_result = execute_remediation(action, severity) 
        
        # Publish incident report to SNS
        report = {
            "alarm_name": alarm_name,
            "alarm_state": alarm_state,
            "reason": reason,
            "claude_analysis": claude_response,
            "remediation_action": action,
            "remediation_result": remediation_result
        }
        
        sns.publish(
            TopicArn=os.environ["SNS_TOPIC_ARN"],
            Subject=f"[{severity.upper()}] Infrastructure Alert: {alarm_name}",
            Message=json.dumps(report, indent=2)
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps(report)
        }
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        sns.publish(
            TopicArn=os.environ["SNS_TOPIC_ARN"],
            Subject="[ERROR] Infrastructure Intelligence System Failure",
            Message=f"Lambda failed to process alarm event.\nError: {str(e)}\nEvent: {json.dumps(event)}"
        )
        raise 
    
def execute_remediation(action, severity):
    cluster = os.environ["ECS_CLUSTER"]
    service = os.environ["ECS_SERVICE"]
    
    try:
        if action == "scale_up":
            current = ecs.describe_services(
                cluster=cluster,
                services=[service]
            )["services"][0]["desiredCount"]
            
            new_count = current + 2
            ecs.update_service(
                cluster=cluster,
                service=service,
                desiredCount=new_count
            )
            return f"Scaled up from {current} to {new_count} tasks"
            
        elif action == "scale_down":
            ecs.update_service(
                cluster=cluster,
                service=service,
                desiredCount=1
            )
            return "Scaled down to 1 task"
            
        elif action == "monitor":
            return "No action taken - monitoring situation"
            
        else:
            return f"Unrecognized action: {action} - no remediation taken"
            
    except Exception as e:
        logger.error(f"Remediation failed: {str(e)}")
        return f"Remediation failed: {str(e)}" 