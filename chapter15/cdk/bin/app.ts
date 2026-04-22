#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { ExpenseAgentStack } from '../lib/expense-agent-stack';

const app = new cdk.App();

new ExpenseAgentStack(app, 'ExpenseAgentStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION ?? 'us-east-1',
  },
  description: '経費精算エージェント インフラストラクチャ',
});
