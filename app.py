from aws_cdk import (
    aws_events as events,
    aws_lambda as lambda_,
    aws_events_targets as targets,
    core,
    aws_s3
)


class LambdaCronStack(core.Stack):
    def __init__(self, app: core.App, id: str) -> None:
        super().__init__(app, id)

        bucket = aws_s3.Bucket(self, "begariver_plots_001", 
            bucket_name = "begariver-plots-001",
            public_read_access = True, 
            removal_policy = core.RemovalPolicy.DESTROY,
            lifecycle_rules = [
                {
                    "transitions": [
                        {
                            "storageClass": aws_s3.StorageClass.INFREQUENT_ACCESS,
                            "transitionAfter": core.Duration.days(30),
                        },
                    ],
                },
            ],
        )

        lambdaFn = lambda_.Function(
            self, "begariver-snapshot",
            code = lambda_.Code.asset('lambda'),
            handler = "lambda-handler.handler",
            timeout = core.Duration.seconds(900),
            runtime = lambda_.Runtime.PYTHON_3_6,
            environment = {
                "s3_bucket_arn" : bucket.bucket_arn,
                "s3_bucket_name" : bucket.bucket_name,
            },
        )

        bucket.grant_read_write(lambdaFn)

        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.rate(core.Duration.hours(1)),
        )
        rule.add_target(targets.LambdaFunction(lambdaFn))


app = core.App()
LambdaCronStack(app, "Begariver-Snapshot")

app.synth()