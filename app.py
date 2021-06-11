from aws_cdk import (
    aws_events as events,
    aws_lambda as lambda_,
    aws_events_targets as targets,
    core,
)


class LambdaCronStack(core.Stack):
    def __init__(self, app: core.App, id: str) -> None:
        super().__init__(app, id)

        with open("lambda-handler.py", encoding="utf8") as fp:
            handler_code = fp.read()

        lambdaFn = lambda_.Function(
            self, "begariver-snapshot",
            code=lambda_.InlineCode(handler_code),
            handler="index.handler",
            timeout=core.Duration.seconds(900),
            runtime=lambda_.Runtime.PYTHON_3_6,
        )

        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.rate(core.Duration.days(1)),
        )
        rule.add_target(targets.LambdaFunction(lambdaFn))


app = core.App()
LambdaCronStack(app, "Lambda-Cron-Delete-AMIs")
app.synth()