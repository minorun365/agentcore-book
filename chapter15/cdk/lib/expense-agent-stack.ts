import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import * as ecrAssets from 'aws-cdk-lib/aws-ecr-assets';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as agentcore from '@aws-cdk/aws-bedrock-agentcore-alpha';
import { ContainerImageBuild } from '@cdklabs/deploy-time-build';
import { Construct } from 'constructs';
import * as dotenv from 'dotenv';
import * as path from 'path';
import * as fs from 'fs';

// .envファイルを読み込み（chapter15/.env）
dotenv.config({
  path: path.join(__dirname, '../../.env'),
});

export class ExpenseAgentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ユーザーデータ読み込み
    const usersJsonPath = path.join(
      __dirname, '../../data/users.json'
    );
    const usersData = this.loadUsersJson(usersJsonPath);
    const emailAddresses = usersData.map(u => u.email);

    // S3バケット（領収書・マスタデータ格納）
    const bucket = new s3.Bucket(this, 'ExpenseAgentBucket', {
      bucketName: `expense-agent-${this.account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // マスタデータをS3にデプロイ
    new s3deploy.BucketDeployment(this, 'DataDeployment', {
      sources: [
        s3deploy.Source.asset(
          path.join(__dirname, '../../data')
        ),
      ],
      destinationBucket: bucket,
      destinationKeyPrefix: 'data',
    });

    // DynamoDBテーブル（承認状態管理）
    const approvalTable = new dynamodb.Table(
      this, 'ApprovalTable', {
        tableName: 'expense-agent-approvals',
        partitionKey: {
          name: 'approval_id',
          type: dynamodb.AttributeType.STRING,
        },
        sortKey: {
          name: 'created_at',
          type: dynamodb.AttributeType.STRING,
        },
        billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
        removalPolicy: cdk.RemovalPolicy.DESTROY,
      },
    );

    // ユーザーごとにSNSトピックを作成
    const snsTopics: Record<string, sns.Topic> = {};
    const snsTopicMap: Record<string, string> = {};

    emailAddresses.forEach((email, i) => {
      const safeEmail = email
        .replace('@', '-at-')
        .replace(/\./g, '-')
        .replace(/\+/g, '-plus-');
      const topic = new sns.Topic(
        this, `NotificationTopic${i}`, {
          topicName: `expense-notification-${safeEmail}`,
          displayName: `経費精算通知: ${email}`,
        },
      );
      topic.addSubscription(
        new subscriptions.EmailSubscription(email)
      );
      snsTopics[email] = topic;
      snsTopicMap[email] = topic.topicArn;
    });

    // Lambda実行ロール（承認コールバック用）
    const lambdaRole = new iam.Role(
      this, 'LambdaExecutionRole', {
        assumedBy: new iam.ServicePrincipal(
          'lambda.amazonaws.com'
        ),
        managedPolicies: [
          iam.ManagedPolicy.fromAwsManagedPolicyName(
            'service-role/AWSLambdaBasicExecutionRole'
          ),
        ],
      },
    );
    approvalTable.grantReadWriteData(lambdaRole);
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      actions: ['sns:Publish'],
      resources: [
        `arn:aws:sns:${this.region}:${this.account}:expense-notification-*`,
      ],
    }));

    // AgentInvoker Lambda用ロール
    const agentInvokerRole = new iam.Role(
      this, 'AgentInvokerRole', {
        assumedBy: new iam.ServicePrincipal(
          'lambda.amazonaws.com'
        ),
        managedPolicies: [
          iam.ManagedPolicy.fromAwsManagedPolicyName(
            'service-role/AWSLambdaBasicExecutionRole'
          ),
        ],
      },
    );
    bucket.grantRead(agentInvokerRole);

    // AgentCoreランタイム実行ロール
    const agentExecutionRole = new iam.Role(
      this, 'AgentExecutionRole', {
        roleName: 'expense-agent-execution-role',
        assumedBy: new iam.CompositePrincipal(
          new iam.ServicePrincipal(
            'bedrock-agentcore.amazonaws.com'
          ),
          new iam.ServicePrincipal(
            'bedrock.amazonaws.com'
          ),
          new iam.ServicePrincipal(
            'lambda.amazonaws.com'
          ),
        ),
        managedPolicies: [
          iam.ManagedPolicy.fromAwsManagedPolicyName(
            'service-role/AWSLambdaBasicExecutionRole'
          ),
        ],
      },
    );
    bucket.grantReadWrite(agentExecutionRole);
    approvalTable.grantReadWriteData(agentExecutionRole);
    agentExecutionRole.addToPolicy(
      new iam.PolicyStatement({
        actions: [
          'bedrock:InvokeModel',
          'bedrock:InvokeModelWithResponseStream',
          'ecr:GetAuthorizationToken',
        ],
        resources: ['*'],
      }),
    );
    agentExecutionRole.addToPolicy(
      new iam.PolicyStatement({
        actions: [
          'logs:DescribeLogStreams',
          'logs:CreateLogGroup',
          'logs:DescribeLogGroups',
          'logs:CreateLogStream',
          'logs:PutLogEvents',
        ],
        resources: [
          `arn:aws:logs:${this.region}:${this.account}:log-group:/aws/bedrock-agentcore/runtimes/*`,
          `arn:aws:logs:${this.region}:${this.account}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*`,
          `arn:aws:logs:${this.region}:${this.account}:log-group:*`,
        ],
      }),
    );
    agentExecutionRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ['sns:Publish'],
        resources: [
          `arn:aws:sns:${this.region}:${this.account}:expense-notification-*`,
        ],
      }),
    );

    // 承認コールバックLambda
    const approvalLambda = new lambda.Function(
      this, 'ApprovalCallbackFunction', {
        functionName: 'expense-agent-approval-callback',
        runtime: lambda.Runtime.PYTHON_3_14,
        handler: 'approval_callback.handler',
        code: lambda.Code.fromAsset(
          path.join(
            __dirname, '../../src/lambda/approval_callback'
          )
        ),
        role: lambdaRole,
        timeout: cdk.Duration.seconds(60),
        environment: {
          APPROVAL_TABLE: approvalTable.tableName,
          AGENT_RUNTIME_NAME: 'expense_agent',
          SNS_TOPIC_MAP: cdk.Fn.toJsonString(snsTopicMap),
        },
      },
    );

    // 承認コールバック用Function URL
    const approvalFunctionUrl = approvalLambda.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ['*'],
        allowedMethods: [
          lambda.HttpMethod.GET,
          lambda.HttpMethod.POST,
        ],
        allowedHeaders: ['Content-Type', 'Authorization'],
      },
    });

    // エージェント用Dockerイメージ
    const agentImage = new ContainerImageBuild(
      this, 'AgentImage', {
        directory: '..',
        file: 'docker/Dockerfile',
        platform: ecrAssets.Platform.LINUX_ARM64,
        exclude: ['cdk', '.git', '.venv', 'node_modules'],
      },
    );
    agentImage.repository.grantPull(agentExecutionRole);

    // エージェントRuntime
    const mainAgentArtifact =
      agentcore.AgentRuntimeArtifact.fromEcrRepository(
        agentImage.repository,
        agentImage.imageTag,
      );

    const agentRuntime = new agentcore.Runtime(
      this, 'ExpenseAgentRuntime', {
        runtimeName: 'expense_agent',
        agentRuntimeArtifact: mainAgentArtifact,
        description: '経費精算エージェント（マルチモーダル解析・分類・承認）',
        executionRole: agentExecutionRole,
        lifecycleConfiguration: {
          idleRuntimeSessionTimeout:
            cdk.Duration.minutes(30),
        },
        environmentVariables: {
          AWS_REGION: 'us-east-1',
          BEDROCK_MODEL_ID: process.env.BEDROCK_MODEL_ID!,
          BUCKET_NAME: bucket.bucketName,
          APPROVAL_TABLE: approvalTable.tableName,
          APPROVAL_API_URL: approvalFunctionUrl.url,
          SNS_TOPIC_MAP: cdk.Fn.toJsonString(snsTopicMap),
          CONFLUENCE_URL: process.env.CONFLUENCE_URL ?? '',
          CONFLUENCE_SPACE_KEY: process.env.CONFLUENCE_SPACE_KEY ?? '',
          CONFLUENCE_USERNAME: process.env.CONFLUENCE_EMAIL ?? '',
          CONFLUENCE_API_TOKEN: process.env.CONFLUENCE_API_TOKEN ?? '',
        },
      },
    );

    // Lambda用ロールにRuntime呼び出し権限を付与
    agentRuntime.grantInvokeRuntime(agentInvokerRole);

    // 承認コールバック用: Runtime呼び出し権限
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      actions: ['bedrock-agentcore:InvokeAgentRuntime'],
      resources: [
        `arn:aws:bedrock-agentcore:${this.region}:${this.account}:runtime/*`,
      ],
    }));
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      actions: ['bedrock-agentcore:ListAgentRuntimes'],
      resources: ['*'],
    }));

    // AgentInvoker Lambda（S3トリガー経由で起動）
    const agentInvokerLambda = new lambda.Function(
      this, 'AgentInvokerFunction', {
        functionName: 'expense-agent-invoker',
        runtime: lambda.Runtime.PYTHON_3_14,
        handler: 'agent_invoker.handler',
        code: lambda.Code.fromAsset(
          path.join(
            __dirname, '../../src/lambda/agent_invoker'
          )
        ),
        role: agentInvokerRole,
        timeout: cdk.Duration.minutes(15),
        environment: {
          AGENT_RUNTIME_ARN:
            agentRuntime.agentRuntimeArn,
          BUCKET_NAME: bucket.bucketName,
        },
      },
    );

    bucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.LambdaDestination(agentInvokerLambda),
      { prefix: 'receipts/' },
    );
  }

  // ユーザーマスタJSONからユーザー情報を読み込む
  private loadUsersJson(
    filePath: string
  ): Array<{ email: string }> {
    const data = JSON.parse(
      fs.readFileSync(filePath, 'utf-8')
    );
    return data.users;
  }
}
