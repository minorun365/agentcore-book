permit(
    principal,
    action == AgentCore::Action::"RefundTarget___process_refund",
    resource == AgentCore::Gateway::"arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/my-gateway"
)
when {
    context.input.amount < 50000
};
