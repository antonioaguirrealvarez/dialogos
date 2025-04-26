https://dev.hume.ai/reference/expression-measurement-api/batch/get-job-predictions

Get job predictions

GET
https://api.hume.ai/v0/batch/jobs/:id/predictions
GET
/v0/batch/jobs/:id/predictions

Python

from hume import HumeClient
client = HumeClient(
    api_key="YOUR_API_KEY",
)
client.expression_measurement.batch.get_job_predictions(
    id="job_id",
)
Try it
200
Retrieved

[
  {
    "source": {
      "type": "url",
      "url": "https://hume-tutorials.s3.amazonaws.com/faces.zip"
    },
    "results": {
      "predictions": [
        {
          "file": "faces/100.jpg",
          "models": {
            "face": {
              "grouped_predictions": [
                {
                  "id": "unknown",
                  "predictions": [
                    {
                      "frame": 0,
                      "time": 0,
                      "prob": 0.9994111061096191,
                      "box": {
                        "x": 1187.885986328125,
                        "y": 1397.697509765625,
                        "w": 1401.668701171875,
                        "h": 1961.424560546875
                      },
                      "emotions": [
                        {
                          "name": "Admiration",
                          "score": 0.10722749680280685
                        },
                        {
                          "name": "Adoration",
                          "score": 0.06395940482616425
                        },
                        {
                          "name": "Aesthetic Appreciation",
                          "score": 0.05811462551355362
                        },
                        {
                          "name": "Amusement",
                          "score": 0.14187128841876984
                        },
                        {
                          "name": "Anger",
                          "score": 0.02804684266448021
                        },
                        {
                          "name": "Anxiety",
                          "score": 0.2713485360145569
                        },
                        {
                          "name": "Awe",
                          "score": 0.33812594413757324
                        },
                        {
                          "name": "Awkwardness",
                          "score": 0.1745193600654602
                        },
                        {
                          "name": "Boredom",
                          "score": 0.23600080609321594
                        },
                        {
                          "name": "Calmness",
                          "score": 0.18988418579101562
                        },
                        {
                          "name": "Concentration",
                          "score": 0.44288986921310425
                        },
                        {
                          "name": "Confusion",
                          "score": 0.39346569776535034
                        },
                        {
                          "name": "Contemplation",
                          "score": 0.31002455949783325
                        },
                        {
                          "name": "Contempt",
                          "score": 0.048870109021663666
                        },
                        {
                          "name": "Contentment",
                          "score": 0.0579497292637825
                        },
                        {
                          "name": "Craving",
                          "score": 0.06544201076030731
                        },
                        {
                          "name": "Desire",
                          "score": 0.05526508390903473
                        },
                        {
                          "name": "Determination",
                          "score": 0.08590991795063019
                        },
                        {
                          "name": "Disappointment",
                          "score": 0.19508258998394012
                        },
                        {
                          "name": "Disgust",
                          "score": 0.031529419124126434
                        },
                        {
                          "name": "Distress",
                          "score": 0.23210826516151428
                        },
                        {
                          "name": "Doubt",
                          "score": 0.3284550905227661
                        },
                        {
                          "name": "Ecstasy",
                          "score": 0.040716782212257385
                        },
                        {
                          "name": "Embarrassment",
                          "score": 0.1467227339744568
                        },
                        {
                          "name": "Empathic Pain",
                          "score": 0.07633581757545471
                        },
                        {
                          "name": "Entrancement",
                          "score": 0.16245244443416595
                        },
                        {
                          "name": "Envy",
                          "score": 0.03267110139131546
                        },
                        {
                          "name": "Excitement",
                          "score": 0.10656816512346268
                        },
                        {
                          "name": "Fear",
                          "score": 0.3115977346897125
                        },
                        {
                          "name": "Guilt",
                          "score": 0.11615975946187973
                        },
                        {
                          "name": "Horror",
                          "score": 0.19795553386211395
                        },
                        {
                          "name": "Interest",
                          "score": 0.3136432468891144
                        },
                        {
                          "name": "Joy",
                          "score": 0.06285581737756729
                        },
                        {
                          "name": "Love",
                          "score": 0.06339752674102783
                        },
                        {
                          "name": "Nostalgia",
                          "score": 0.05866732448339462
                        },
                        {
                          "name": "Pain",
                          "score": 0.07684041559696198
                        },
                        {
                          "name": "Pride",
                          "score": 0.026822954416275024
                        },
                        {
                          "name": "Realization",
                          "score": 0.30000734329223633
                        },
                        {
                          "name": "Relief",
                          "score": 0.04414166510105133
                        },
                        {
                          "name": "Romance",
                          "score": 0.042728863656520844
                        },
                        {
                          "name": "Sadness",
                          "score": 0.14773206412792206
                        },
                        {
                          "name": "Satisfaction",
                          "score": 0.05902980640530586
                        },
                        {
                          "name": "Shame",
                          "score": 0.08103451132774353
                        },
                        {
                          "name": "Surprise (negative)",
                          "score": 0.25518184900283813
                        },
                        {
                          "name": "Surprise (positive)",
                          "score": 0.28845661878585815
                        },
                        {
                          "name": "Sympathy",
                          "score": 0.062488824129104614
                        },
                        {
                          "name": "Tiredness",
                          "score": 0.1559651643037796
                        },
                        {
                          "name": "Triumph",
                          "score": 0.01955239288508892
                        }
                      ],
                      "facs": null,
                      "descriptions": null
                    }
                  ]
                }
              ],
              "metadata": null
            }
          }
        }
      ],
      "errors": []
    }
  }
]
Get the JSON predictions of a completed inference job.

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
source
object

Hide 3 variants
url
object

Hide 2 properties
type
"url"
url
string
The URL of the source media file.

OR
file
object
The list of files submitted for analysis.


Hide 4 properties
type
"file"
md5sum
string
The MD5 checksum of the file.

content_type
string
Optional
The content type of the file.

filename
string
Optional
The name of the file.

OR
text
object

Hide 1 properties
type
"text"
results
object
Optional

Hide 2 properties
predictions
list of objects

Hide 2 properties
file
string
A file path relative to the top level source URL or file.

models
object

Hide 6 properties
face
object
Optional

Hide 2 properties
grouped_predictions
list of objects

Show 2 properties
metadata
map from strings to any
Optional
No associated metadata for this model. Value will be null.

burst
object
Optional

Hide 2 properties
grouped_predictions
list of objects

Show 2 properties
metadata
map from strings to any
Optional
No associated metadata for this model. Value will be null.

prosody
object
Optional

Hide 2 properties
grouped_predictions
list of objects

Hide 2 properties
id
string
An automatically generated label to identify individuals in your media file. Will be unknown if you have chosen to disable identification, or if the model is unable to distinguish between individuals.

predictions
list of objects

Hide 5 properties
time
object
A time range with a beginning and end, measured in seconds.


Hide 2 properties
begin
double
Beginning of time range in seconds.

end
double
End of time range in seconds.

emotions
list of objects
A high-dimensional embedding in emotion space.


Hide 2 properties
name
string
Name of the emotion being expressed.

score
double
Embedding value for the emotion being expressed.

text
string
Optional
A segment of text (like a word or a sentence).

confidence
double
Optional
Value between 0.0 and 1.0 that indicates our transcription model’s relative confidence in this text.

speaker_confidence
double
Optional
Value between 0.0 and 1.0 that indicates our transcription model’s relative confidence that this text was spoken by this speaker.

metadata
object
Optional
Transcription metadata for your media file.


Hide 2 properties
confidence
double
Value between 0.0 and 1.0 indicating our transcription model’s relative confidence in the transcription of your media file.

detected_language
enum
Optional

Show 29 enum values
language
object
Optional

Hide 2 properties
grouped_predictions
list of objects

Hide 2 properties
id
string
An automatically generated label to identify individuals in your media file. Will be unknown if you have chosen to disable identification, or if the model is unable to distinguish between individuals.

predictions
list of objects

Hide 8 properties
text
string
A segment of text (like a word or a sentence).

position
object
Position of a segment of text within a larger document, measured in characters. Uses zero-based indexing. The beginning index is inclusive and the end index is exclusive.


Show 2 properties
emotions
list of objects
A high-dimensional embedding in emotion space.


Hide 2 properties
name
string
Name of the emotion being expressed.

score
double
Embedding value for the emotion being expressed.

time
object
Optional
A time range with a beginning and end, measured in seconds.


Hide 2 properties
begin
double
Beginning of time range in seconds.

end
double
End of time range in seconds.

confidence
double
Optional
Value between 0.0 and 1.0 that indicates our transcription model’s relative confidence in this text.

speaker_confidence
double
Optional
Value between 0.0 and 1.0 that indicates our transcription model’s relative confidence that this text was spoken by this speaker.

sentiment
list of objects
Optional
Sentiment predictions returned as a distribution. This model predicts the probability that a given text could be interpreted as having each sentiment level from 1 (negative) to 9 (positive).

Compared to returning one estimate of sentiment, this enables a more nuanced analysis of a text’s meaning. For example, a text with very neutral sentiment would have an average rating of 5. But also a text that could be interpreted as having very positive sentiment or very negative sentiment would also have an average rating of 5. The average sentiment is less informative than the distribution over sentiment, so this API returns a value for each sentiment level.


Hide 2 properties
name
string
Level of sentiment, ranging from 1 (negative) to 9 (positive)

score
double
Prediction for this level of sentiment

toxicity
list of objects
Optional
Toxicity predictions returned as probabilities that the text can be classified into the following categories: toxic, severe_toxic, obscene, threat, insult, and identity_hate.


Hide 2 properties
name
string
Category of toxicity.

score
double
Prediction for this category of toxicity

metadata
object
Optional
Transcription metadata for your media file.


Show 2 properties
ner
object
Optional

Hide 2 properties
grouped_predictions
list of objects

Hide 2 properties
id
string
An automatically generated label to identify individuals in your media file. Will be unknown if you have chosen to disable identification, or if the model is unable to distinguish between individuals.

predictions
list of objects

Hide 10 properties
entity
string
The recognized topic or entity.

position
object
Position of a segment of text within a larger document, measured in characters. Uses zero-based indexing. The beginning index is inclusive and the end index is exclusive.


Show 2 properties
entity_confidence
double
Our NER model’s relative confidence in the recognized topic or entity.

support
double
A measure of how often the entity is linked to by other entities.

uri
string
A URL which provides more information about the recognized topic or entity.

link_word
string
The specific word to which the emotion predictions are linked.

emotions
list of objects
A high-dimensional embedding in emotion space.


Show 2 properties
time
object
Optional
A time range with a beginning and end, measured in seconds.


Show 2 properties
confidence
double
Optional
Value between 0.0 and 1.0 that indicates our transcription model’s relative confidence in this text.

speaker_confidence
double
Optional
Value between 0.0 and 1.0 that indicates our transcription model’s relative confidence that this text was spoken by this speaker.

metadata
object
Optional
Transcription metadata for your media file.


Hide 2 properties
confidence
double
Value between 0.0 and 1.0 indicating our transcription model’s relative confidence in the transcription of your media file.

detected_language
enum
Optional

Search...

zh
da
nl
en
en-AU
en-IN
en-NZ
en-GB
fr
fr-CA
de
hi
hi-Latn
id
it
ja
ko
no
pl
pt
pt-BR
pt-PT
ru
es
es-419
sv
ta
tr
uk
facemesh
object
Optional

Show 2 properties
errors
list of objects

Hide 2 properties
message
string
An error message.

file
string
A file path relative to the top level source URL or file.

error
string
Optional
An error message.