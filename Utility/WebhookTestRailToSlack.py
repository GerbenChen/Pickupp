from slack_sdk.webhook import WebhookClient
import time
url = "https://hooks.slack.com/services/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"
webhook = WebhookClient(url)

def WebHookSendResult(TestSuiteName,TotalResult,FailCase,TestResultLink):
    response = webhook.send(
        text="fallback",
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Test Suite : %s" % TestSuiteName
                }
            },
            {
                "type": "section",
                "fields": [ {
                    "type": "mrkdwn",
                    "text": ">*PASS* : %s\n>*FAIL* : %s" % (TotalResult[0],TotalResult[1]),
                },
                {
					"type": "mrkdwn",
					"text": "*TestResultLink:*\n<%s|Link Is Here>" % TestResultLink
				},
                {
                    "type": "mrkdwn",
                    "text": "%s" % FailCase,
                }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Create at*\n<!date^%s^Posted {date_num} {time_secs}|Posted PST>" % int(time.time())
                }
            }
        ]
    )


                