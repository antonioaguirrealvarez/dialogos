https://dev.hume.ai/docs/expression-measurement/rest


Processing batches of media files


Copy page

Hume’s Expression Measurement API is designed to facilitate large-scale processing of files using Hume’s advanced models through an asynchronous, job-based interface. This API allows developers to submit jobs for parallel processing of various files, enabling efficient handling of multiple data points simultaneously, and receiving notifications when results are available.

Key features
Asynchronous job submission: Jobs can be submitted to process a wide array of files in parallel, making it ideal for applications that require the analysis of large volumes of data.

Flexible data input options: The API supports multiple data formats, including hosted file URLs, local files directly from your system, and raw text in the form of a list of strings. This versatility ensures that you can easily integrate the API into their applications, regardless of where their data resides.

Applications and use cases
Hume’s Expression Measurement API is particularly useful for leveraging Hume’s expressive models across a broad spectrum of files and formats. Whether it’s for processing large datasets for research, analyzing customer feedback across multiple channels, or enriching user experiences in media-rich applications, REST provides a robust solution for asynchronously handling complex, data-intensive tasks.

Using Hume’s Expression Measurement API
Here we’ll show you how to upload your own files and run Hume models on batches of data. If you haven’t already, grab your API Key.

1
Making a request to the API
Start a new job with the Expression Measurement API.


cURL

Hume Python SDK

import asyncio
from hume import AsyncHumeClient
from hume.expression_measurement.batch import Face, Models
async def main():
    # Initialize an authenticated client
    client = AsyncHumeClient(api_key=<YOUR_API_KEY>)
    # Define the URL(s) of the files you would like to analyze
    job_urls = ["https://hume-tutorials.s3.amazonaws.com/faces.zip"]
    # Create configurations for each model you would like to use (blank = default)
    face_config = Face()
    # Create a Models object
    models_chosen = Models(face=face_config)
    # Start an inference job and print the job_id
    job_id = await client.expression_measurement.batch.start_inference_job(
        urls=job_urls, models=models_chosen
    )
    print(job_id)
if __name__ == "__main__":
    asyncio.run(main())
To do the same with a local file:


cURL

Hume Python SDK

import asyncio
from hume import AsyncHumeClient
from hume.expression_measurement.batch import Face, Models
from hume.expression_measurement.batch.types import InferenceBaseRequest
async def main():
    # Initialize an authenticated client
    client = AsyncHumeClient(api_key=<YOUR_API_KEY>)
    # Define the filepath(s) of the file(s) you would like to analyze
    local_filepaths = [
        open("faces.zip", mode="rb"),
        open("david_hume.jpeg", mode="rb")
    ]
    # Create configurations for each model you would like to use (blank = default)
    face_config = Face()
    # Create a Models object
    models_chosen = Models(face=face_config)
    
    # Create a stringified object containing the configuration
    stringified_configs = InferenceBaseRequest(models=models_chosen)
    # Start an inference job and print the job_id
    job_id = await client.expression_measurement.batch.start_inference_job_from_local_file(
        json=stringified_configs, file=local_filepaths
    )
    print(job_id)
if __name__ == "__main__":
    asyncio.run(main())
Sample files for you to use in this tutorial are available here: Download faces.zip Download david_hume.jpeg

2
Checking job status
Use webhooks to asynchronously receive notifications once the job completes. It is not recommended to poll the API periodically for job status.

There are several ways to get notified and check the status of your job.

Using the Get job details API endpoint.
Providing a callback URL. We will send a POST request to your URL when the job is complete. Your request body should look like this: { "callback_url": "<YOUR CALLBACK URL>" }
JSON

{
    job_id: "Job ID",
    status: "STATUS (COMPLETED/FAILED)",
    predictions: [ARRAY OF RESULTS]
}
3
Retrieving predictions
Your predictions are available in a few formats.

To get predictions as JSON use the Get job predictions endpoint.


cURL

Hume Python SDK

import asyncio
from hume import AsyncHumeClient
client = AsyncHumeClient(api_key="<YOUR_API_KEY>")
async def main():
    job_predictions = await client.expression_measurement.batch.get_job_predictions(
        id="<YOUR_JOB_ID>"
    )
if __name__ == "__main__":
    asyncio.run(main())
To get predictions as a compressed file of CSVs, one per model use the Get job artifacts endpoint.


cURL

Hume Python SDK

import asyncio
from hume import AsyncHumeClient
client = AsyncHumeClient(api_key="<YOUR_API_KEY>")
async def main():
    with open("artifacts.zip", "wb") as f:
        async for new_bytes in client.expression_measurement.batch.get_job_artifacts("<YOUR_JOB_ID>"):
            f.write(new_bytes)
if __name__ == "__main__":
    asyncio.run(main())
API limits
The size of any individual file provided by URL cannot exceed 1 GB.
The size of any individual local file cannot exceed 100 MB.
Each request has an upper limit of 100 URLs, 100 strings (raw text), and 100 local media files. Can be a mix of the media files or archives (.zip, .tar.gz, .tar.bz2, .tar.xz).
For audio and video files the max length supported is 3 hours.
The limit for each individual text string for the Expression Measurement API is 255 MB.
The limit to the number of jobs that can be queued at a time is 500.
Providing URLs and files
You can provide data for your job in one of the following formats: hosted file URLs, local files, or raw text presented as a list of strings.

In this tutorial, the data is publicly available to download. For added security, you may choose to create a signed URL through your preferred cloud storage provider.

Cloud Provider	Signing URLs
GCP	https://cloud.google.com/storage/docs/access-control/signed-urls
AWS	https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-signed-urls.html
Azure	https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview
