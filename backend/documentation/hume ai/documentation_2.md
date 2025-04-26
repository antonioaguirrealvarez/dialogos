https://dev.hume.ai/reference/expression-measurement-api/batch/get-job-details

Get job details

GET
https://api.hume.ai/v0/batch/jobs/:id
GET
/v0/batch/jobs/:id

Python

from hume import HumeClient
client = HumeClient(
    api_key="YOUR_API_KEY",
)
client.expression_measurement.batch.get_job_details(
    id="job_id",
)
Try it
200
Inference

{
  "job_id": "job_id",
  "request": {
    "files": [],
    "models": {
      "face": {
        "fps_pred": 3,
        "prob_threshold": 0.99,
        "identify_faces": false,
        "min_face_size": 60,
        "facs": null,
        "descriptions": null,
        "save_faces": false
      },
      "burst": {},
      "prosody": {
        "granularity": "utterance",
        "window": null,
        "identify_speakers": false
      },
      "language": {
        "granularity": "word",
        "sentiment": null,
        "toxicity": null,
        "identify_speakers": false
      },
      "ner": {
        "identify_speakers": false
      },
      "facemesh": {}
    },
    "urls": [
      "https://hume-tutorials.s3.amazonaws.com/faces.zip"
    ],
    "text": [],
    "callback_url": null,
    "notify": true
  },
  "state": {
    "status": "COMPLETED",
    "created_timestamp_ms": 1712590457884,
    "ended_timestamp_ms": 1712590462252,
    "num_errors": 0,
    "num_predictions": 10,
    "started_timestamp_ms": 1712590457995
  },
  "type": "INFERENCE"
}
Get the request details and state of a given job.

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
job_id
string
format: "uuid"
The ID associated with this job.

request
object
The request that initiated the job.


Hide 7 properties
files
list of objects

Hide 3 properties
md5sum
string
The MD5 checksum of the file.

filename
string
Optional
The name of the file.

content_type
string
Optional
The content type of the file.

models
object
Optional
The models used for inference.


Hide 6 properties
face
object
Optional
The Facial Emotional Expression model analyzes human facial expressions in images and videos. Results will be provided per frame for video files.

Recommended input file types: .png, .jpeg, .mp4


Hide 7 properties
fps_pred
double
Optional
Defaults to 3
Number of frames per second to process. Other frames will be omitted from the response. Set to 0 to process every frame.

prob_threshold
double
Optional
>=0
<=1
Defaults to 0.99
Face detection probability threshold. Faces detected with a probability less than this threshold will be omitted from the response.

identify_faces
boolean
Optional
Defaults to false
Whether to return identifiers for faces across frames. If true, unique identifiers will be assigned to face bounding boxes to differentiate different faces. If false, all faces will be tagged with an unknown ID.

min_face_size
uint64
Optional
Minimum bounding box side length in pixels to treat as a face. Faces detected with a bounding box side length in pixels less than this threshold will be omitted from the response.

facs
map from strings to any
Optional
To include predictions for this model type, set this field to {}. It is currently not configurable further.

descriptions
map from strings to any
Optional
To include predictions for this model type, set this field to {}. It is currently not configurable further.

save_faces
boolean
Optional
Defaults to false
Whether to extract and save the detected faces in the artifacts zip created by each job.

burst
map from strings to any
Optional
To include predictions for this model type, set this field to {}. It is currently not configurable further.

prosody
object
Optional
The Speech Prosody model analyzes the intonation, stress, and rhythm of spoken word.

Recommended input file types: .wav, .mp3, .mp4


Hide 3 properties
granularity
enum
Optional
The granularity at which to generate predictions. The granularity field is ignored if transcription is not enabled or if the window field has been set.

word: At the word level, our model provides a separate output for each word, offering the most granular insight into emotional expression during speech.

sentence: At the sentence level of granularity, we annotate the emotional tone of each spoken sentence with our Prosody and Emotional Language models.

utterance: Utterance-level granularity is between word- and sentence-level. It takes into account natural pauses or breaks in speech, providing more rapidly updated measures of emotional expression within a flowing conversation. For text inputs, utterance-level granularity will produce results identical to sentence-level granularity.

conversational_turn: Conversational turn-level granularity provides a distinct output for each change in speaker. It captures the full sequence of words and sentences spoken uninterrupted by each person. This approach provides a higher-level view of the emotional dynamics in a multi-participant dialogue. For text inputs, specifying conversational turn-level granularity for our Emotional Language model will produce results for the entire passage.

Allowed values:
word
sentence
utterance
conversational_turn
window
object
Optional
Generate predictions based on time.

Setting the window field allows for a ‘sliding window’ approach, where a fixed-size window moves across the audio or video file in defined steps. This enables continuous analysis of prosody within subsets of the file, providing dynamic and localized insights into emotional expression.


Show 2 properties
identify_speakers
boolean
Optional
Defaults to false
Whether to return identifiers for speakers over time. If true, unique identifiers will be assigned to spoken words to differentiate different speakers. If false, all speakers will be tagged with an unknown ID.

language
object
Optional
The Emotional Language model analyzes passages of text. This also supports audio and video files by transcribing and then directly analyzing the transcribed text.

Recommended input filetypes: .txt, .mp3, .wav, .mp4


Hide 4 properties
granularity
enum
Optional
The granularity at which to generate predictions. The granularity field is ignored if transcription is not enabled or if the window field has been set.

word: At the word level, our model provides a separate output for each word, offering the most granular insight into emotional expression during speech.

sentence: At the sentence level of granularity, we annotate the emotional tone of each spoken sentence with our Prosody and Emotional Language models.

utterance: Utterance-level granularity is between word- and sentence-level. It takes into account natural pauses or breaks in speech, providing more rapidly updated measures of emotional expression within a flowing conversation. For text inputs, utterance-level granularity will produce results identical to sentence-level granularity.

conversational_turn: Conversational turn-level granularity provides a distinct output for each change in speaker. It captures the full sequence of words and sentences spoken uninterrupted by each person. This approach provides a higher-level view of the emotional dynamics in a multi-participant dialogue. For text inputs, specifying conversational turn-level granularity for our Emotional Language model will produce results for the entire passage.

Allowed values:
word
sentence
utterance
conversational_turn
sentiment
map from strings to any
Optional
To include predictions for this model type, set this field to {}. It is currently not configurable further.

toxicity
map from strings to any
Optional
To include predictions for this model type, set this field to {}. It is currently not configurable further.

identify_speakers
boolean
Optional
Defaults to false
Whether to return identifiers for speakers over time. If true, unique identifiers will be assigned to spoken words to differentiate different speakers. If false, all speakers will be tagged with an unknown ID.

ner
object
Optional
The NER (Named-entity Recognition) model identifies real-world objects and concepts in passages of text. This also supports audio and video files by transcribing and then directly analyzing the transcribed text.

Recommended input filetypes: .txt, .mp3, .wav, .mp4


Hide 1 properties
identify_speakers
boolean
Optional
Defaults to false
Whether to return identifiers for speakers over time. If true, unique identifiers will be assigned to spoken words to differentiate different speakers. If false, all speakers will be tagged with an unknown ID.

facemesh
map from strings to any
Optional
To include predictions for this model type, set this field to {}. It is currently not configurable further.

transcription
object
Optional
Transcription-related configuration options.

To disable transcription, explicitly set this field to null.


Hide 3 properties
language
enum
Optional
By default, we use an automated language detection method for our Speech Prosody, Language, and NER models. However, if you know what language is being spoken in your media samples, you can specify it via its BCP-47 tag and potentially obtain more accurate results.

You can specify any of the following languages:

Chinese: zh
Danish: da
Dutch: nl
English: en
English (Australia): en-AU
English (India): en-IN
English (New Zealand): en-NZ
English (United Kingdom): en-GB
French: fr
French (Canada): fr-CA
German: de
Hindi: hi
Hindi (Roman Script): hi-Latn
Indonesian: id
Italian: it
Japanese: ja
Korean: ko
Norwegian: no
Polish: pl
Portuguese: pt
Portuguese (Brazil): pt-BR
Portuguese (Portugal): pt-PT
Russian: ru
Spanish: es
Spanish (Latin America): es-419
Swedish: sv
Tamil: ta
Turkish: tr
Ukrainian: uk

Show 29 enum values
identify_speakers
boolean
Optional
Defaults to false
Whether to return identifiers for speakers over time. If true, unique identifiers will be assigned to spoken words to differentiate different speakers. If false, all speakers will be tagged with an unknown ID.

confidence_threshold
double
Optional
>=0
<=1
Defaults to 0.5
Transcript confidence threshold. Transcripts generated with a confidence less than this threshold will be considered invalid and not used as an input for model inference.

urls
list of strings
Optional
URLs to the media files to be processed. Each must be a valid public URL to a media file (see recommended input filetypes) or an archive (.zip, .tar.gz, .tar.bz2, .tar.xz) of media files.

If you wish to supply more than 100 URLs, consider providing them as an archive (.zip, .tar.gz, .tar.bz2, .tar.xz).

text
list of strings
Optional
Text to supply directly to our language and NER models.

callback_url
string
Optional
If provided, a POST request will be made to the URL with the generated predictions on completion or the error message on failure.

notify
boolean
Optional
Defaults to false
Whether to send an email notification to the user upon job completion/failure.

state
object
The current state of the job.


Hide 4 variants
QUEUED
object

Hide 2 properties
status
"QUEUED"
created_timestamp_ms
long
When this job was created (Unix timestamp in milliseconds).

OR
IN_PROGRESS
object

Hide 3 properties
status
"IN_PROGRESS"
created_timestamp_ms
long
When this job was created (Unix timestamp in milliseconds).

started_timestamp_ms
long
When this job started (Unix timestamp in milliseconds).

OR
COMPLETED
object

Hide 6 properties
status
"COMPLETED"
created_timestamp_ms
long
When this job was created (Unix timestamp in milliseconds).

ended_timestamp_ms
long
When this job ended (Unix timestamp in milliseconds).

num_errors
uint64
The number of errors that occurred while running this job.

num_predictions
uint64
The number of predictions that were generated by this job.

started_timestamp_ms
long
When this job started (Unix timestamp in milliseconds).

OR
FAILED
object

Hide 5 properties
status
"FAILED"
created_timestamp_ms
long
When this job was created (Unix timestamp in milliseconds).

ended_timestamp_ms
long
When this job ended (Unix timestamp in milliseconds).

message
string
An error message.

started_timestamp_ms
long
When this job started (Unix timestamp in milliseconds).

type
string
Denotes the job type.

Jobs created with the Expression Measurement API will have this field set to INFERENCE.