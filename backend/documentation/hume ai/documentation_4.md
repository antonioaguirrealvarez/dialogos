https://dev.hume.ai/reference/expression-measurement-api/batch/get-job-artifacts


Get job artifacts

GET
https://api.hume.ai/v0/batch/jobs/:id/artifacts
GET
/v0/batch/jobs/:id/artifacts

curl https://api.hume.ai/v0/batch/jobs/id/artifacts \
     -H "X-Hume-Api-Key: <apiKey>"
Try it
Get the artifacts ZIP of a completed inference job.

Path parameters
id
string
Required
The unique identifier for the job.

Headers
X-Hume-Api-Key
string
Required
Response