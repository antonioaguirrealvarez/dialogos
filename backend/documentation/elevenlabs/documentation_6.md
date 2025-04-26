Create transcript

POST

https://api.elevenlabs.io
/v1/speech-to-text
POST
/v1/speech-to-text

Python

from elevenlabs import ElevenLabs
client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.speech_to_text.convert(
    model_id="model_id",
)
Try it

200
Successful

{
  "language_code": "en",
  "language_probability": 0.98,
  "text": "Hello world!",
  "words": [
    {
      "text": "Hello",
      "type": "word",
      "start": 0,
      "end": 0.5,
      "speaker_id": "speaker_1",
      "characters": [
        {
          "text": "text",
          "start": 0,
          "end": 0.1
        }
      ]
    },
    {
      "text": " ",
      "type": "spacing",
      "start": 0.5,
      "end": 0.5,
      "speaker_id": "speaker_1",
      "characters": [
        {
          "text": "text",
          "start": 0,
          "end": 0.1
        }
      ]
    },
    {
      "text": "world!",
      "type": "word",
      "start": 0.5,
      "end": 1.2,
      "speaker_id": "speaker_1",
      "characters": [
        {
          "text": "text",
          "start": 0,
          "end": 0.1
        }
      ]
    }
  ],
  "additional_formats": [
    {
      "requested_format": "requested_format",
      "file_extension": "file_extension",
      "content_type": "content_type",
      "is_base64_encoded": true,
      "content": "content"
    }
  ]
}
Transcribe an audio or video file.

Headers
xi-api-key
string
Required
Query parameters
enable_logging
boolean
Optional
Defaults to true
When enable_logging is set to false zero retention mode will be used for the request. This will mean history features are unavailable for this request, including request stitching. Zero retention mode may only be used by enterprise customers.

Request
This endpoint expects a multipart form containing an optional file.
model_id
string
Required
The ID of the model to use for transcription, currently only ‘scribe_v1’ and ‘scribe_v1_experimental’ are available.

file
file
Optional
The file to transcribe. All major audio and video formats are supported. Exactly one of the file or cloud_storage_url parameters must be provided. The file size must be less than 1GB.

language_code
string
Optional
An ISO-639-1 or ISO-639-3 language_code corresponding to the language of the audio file. Can sometimes improve transcription performance if known beforehand. Defaults to null, in this case the language is predicted automatically.

tag_audio_events
boolean
Optional
Defaults to true
Whether to tag audio events like (laughter), (footsteps), etc. in the transcription.

num_speakers
integer
Optional
>=1
<=32
The maximum amount of speakers talking in the uploaded file. Can help with predicting who speaks when. The maximum amount of speakers that can be predicted is 32. Defaults to null, in this case the amount of speakers is set to the maximum value the model supports.

timestamps_granularity
enum
Optional
Defaults to word
The granularity of the timestamps in the transcription. ‘word’ provides word-level timestamps and ‘character’ provides character-level timestamps per word.

Allowed values:
none
word
character
diarize
boolean
Optional
Defaults to false
Whether to annotate which speaker is currently talking in the uploaded file.

additional_formats
list of objects
Optional
A list of additional formats to export the transcript to.


Hide 6 variants
docx
object
Required

Show 6 properties
OR
html
object
Required

Show 6 properties
OR
pdf
object
Required

Show 6 properties
OR
segmented_json
object
Required

Hide 6 properties
format
"segmented_json"
Required
include_speakers
boolean
Optional
Defaults to true
include_timestamps
boolean
Optional
Defaults to true
max_segment_chars
integer
Optional
max_segment_duration_s
double
Optional
segment_on_silence_longer_than_s
double
Optional
OR
srt
object
Required

Show 7 properties
OR
txt
object
Required

Hide 7 properties
format
"txt"
Required
include_speakers
boolean
Optional
Defaults to true
include_timestamps
boolean
Optional
Defaults to true
max_characters_per_line
integer
Optional
max_segment_chars
integer
Optional
max_segment_duration_s
double
Optional
segment_on_silence_longer_than_s
double
Optional
file_format
enum
Optional
Defaults to other
The format of input audio. Options are ‘pcm_s16le_16’ or ‘other’ For pcm_s16le_16, the input audio must be 16-bit PCM at a 16kHz sample rate, single channel (mono), and little-endian byte order. Latency will be lower than with passing an encoded waveform.

Allowed values:
pcm_s16le_16
other
cloud_storage_url
string
Optional
The valid AWS S3, Cloudflare R2 or Google Cloud Storage URL of the file to transcribe. Exactly one of the file or cloud_storage_url parameters must be provided. The file must be a valid publicly accessible cloud storage URL. The file size must be less than 2GB. URL can be pre-signed.

Response
Successful Response

language_code
string
The detected language code (e.g. ‘eng’ for English).

language_probability
double
The confidence score of the language detection (0 to 1).

text
string
The raw text of the transcription.

words
list of objects
List of words with their timing information.


Hide 6 properties
text
string
The word or sound that was transcribed.

type
enum
The type of the word or sound. ‘audio_event’ is used for non-word sounds like laughter or footsteps.

Allowed values:
word
spacing
audio_event
start
double
Optional
The start time of the word or sound in seconds.

end
double
Optional
The end time of the word or sound in seconds.

speaker_id
string
Optional
Unique identifier for the speaker of this word.

characters
list of objects
Optional
The characters that make up the word and their timing information.


Hide 3 properties
text
string
The character that was transcribed.

start
double
Optional
The start time of the character in seconds.

end
double
Optional
The end time of the character in seconds.

additional_formats
list of optional objects
Optional
Requested additional formats of the transcript.


Hide 5 properties
requested_format
string
The requested format.

file_extension
string
The file extension of the additional format.

content_type
string
The content type of the additional format.

is_base64_encoded
boolean
Whether the content is base64 encoded.

content
string
The content of the additional format.

Errors

422
Speech to Text Convert Request Unprocessable Entity Error
Was this page helpful?
Yes
