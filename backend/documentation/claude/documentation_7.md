Using the API
Getting started
​
Accessing the API
The API is made available via our web Console. You can use the Workbench to try out the API in the browser and then generate API keys in Account Settings. Use workspaces to segment your API keys and control spend by use case.

​
Authentication
All requests to the Anthropic API must include an x-api-key header with your API key. If you are using the Client SDKs, you will set the API when constructing a client, and then the SDK will send the header on your behalf with every request. If integrating directly with the API, you’ll need to send this header yourself.

​
Content types
The Anthropic API always accepts JSON in request bodies and returns JSON in response bodies. You will need to send the content-type: application/json header in requests. If you are using the Client SDKs, this will be taken care of automatically.

​
Response Headers
The Anthropic API includes the following headers in every response:

request-id: A globally unique identifier for the request.

anthropic-organization-id: The organization ID associated with the API key used in the request.

​
Examples
curl
Python
TypeScript
Install via PyPI:


pip install anthropic
Python

import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="my_api_key",
)
message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)
print(message.content)


Errors
​
HTTP errors
Our API follows a predictable HTTP error code format:

400 - invalid_request_error: There was an issue with the format or content of your request. We may also use this error type for other 4XX status codes not listed below.

401 - authentication_error: There’s an issue with your API key.

403 - permission_error: Your API key does not have permission to use the specified resource.

404 - not_found_error: The requested resource was not found.

413 - request_too_large: Request exceeds the maximum allowed number of bytes.

429 - rate_limit_error: Your account has hit a rate limit.

500 - api_error: An unexpected error has occurred internal to Anthropic’s systems.

529 - overloaded_error: Anthropic’s API is temporarily overloaded.

Sudden large increases in usage may lead to an increased rate of 529 errors. We recommend ramping up gradually and maintaining consistent usage patterns.

When receiving a streaming response via SSE, it’s possible that an error can occur after returning a 200 response, in which case error handling wouldn’t follow these standard mechanisms.

​
Error shapes
Errors are always returned as JSON, with a top-level error object that always includes a type and message value. For example:

JSON

{
  "type": "error",
  "error": {
    "type": "not_found_error",
    "message": "The requested resource could not be found."
  }
}
In accordance with our versioning policy, we may expand the values within these objects, and it is possible that the type values will grow over time.

​
Request id
Every API response includes a unique request-id header. This header contains a value such as req_018EeWyXxfu5pfWkrYcMdjWG. When contacting support about a specific request, please include this ID to help us quickly resolve your issue.

Our official SDKs provide this value as a property on top-level response objects, containing the value of the x-request-id header:


Python

TypeScript

import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

const message = await client.messages.create({
  model: 'claude-3-7-sonnet-20250219',
  max_tokens: 1024,
  messages: [
    {"role": "user", "content": "Hello, Claude"}
  ]
});
console.log('Request ID:', message._request_id);
​
Long requests
We highly encourage using the streaming Messages API or Message Batches API for long running requests, especially those over 10 minutes.

We do not recommend setting a large max_tokens values without using our streaming Messages API or Message Batches API:

Some networks may drop idle connections after a variable period of time, which can cause the request to fail or timeout without receiving a response from Anthropic.
Networks differ in reliablity; our Message Batches API can help you manage the risk of network issues by allowing you to poll for results rather than requiring an uninterrupted network connection.
If you are building a direct API integration, you should be aware that setting a TCP socket keep-alive can reduce the impact of idle connection timeouts on some networks.

Our SDKs will validate that your non-streaming Messages API requests are not expected to exceed a 10 minute timeout and also will set a socket option for TCP keep-alive.

Messages
Send a structured list of input messages with text and/or image content, and the model will generate the next message in the conversation.

The Messages API can be used for either single queries or stateless multi-turn conversations.

Learn more about the Messages API in our user guide

POST
/
v1
/
messages
Headers
​
anthropic-beta
string[]
Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like beta1,beta2 or specify the header multiple times for each beta.

​
anthropic-version
string
required
The version of the Anthropic API you want to use.

Read more about versioning and our version history here.

​
x-api-key
string
required
Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the Console. Each key is scoped to a Workspace.

Body
application/json
​
max_tokens
integer
required
The maximum number of tokens to generate before stopping.

Note that our models may stop before reaching this maximum. This parameter only specifies the absolute maximum number of tokens to generate.

Different models have different maximum values for this parameter. See models for details.

Required range: x > 1
​
messages
object[]
required
Input messages.

Our models are trained to operate on alternating user and assistant conversational turns. When creating a new Message, you specify the prior conversational turns with the messages parameter, and the model then generates the next Message in the conversation. Consecutive user or assistant turns in your request will be combined into a single turn.

Each input message must be an object with a role and content. You can specify a single user-role message, or you can include multiple user and assistant messages.

If the final message uses the assistant role, the response content will continue immediately from the content in that message. This can be used to constrain part of the model's response.

Example with a single user message:

[{"role": "user", "content": "Hello, Claude"}]
Example with multiple conversational turns:

[
  {"role": "user", "content": "Hello there."},
  {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
  {"role": "user", "content": "Can you explain LLMs in plain English?"},
]
Example with a partially-filled response from Claude:

[
  {"role": "user", "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"},
  {"role": "assistant", "content": "The best answer is ("},
]
Each input message content may be either a single string or an array of content blocks, where each block has a specific type. Using a string for content is shorthand for an array of one content block of type "text". The following input messages are equivalent:

{"role": "user", "content": "Hello, Claude"}
{"role": "user", "content": [{"type": "text", "text": "Hello, Claude"}]}
Starting with Claude 3 models, you can also send image content blocks:

{"role": "user", "content": [
  {
    "type": "image",
    "source": {
      "type": "base64",
      "media_type": "image/jpeg",
      "data": "/9j/4AAQSkZJRg...",
    }
  },
  {"type": "text", "text": "What is in this image?"}
]}
We currently support the base64 source type for images, and the image/jpeg, image/png, image/gif, and image/webp media types.

See examples for more input examples.

Note that if you want to include a system prompt, you can use the top-level system parameter — there is no "system" role for input messages in the Messages API.

There is a limit of 100000 messages in a single request.


Show child attributes

​
model
string
required
The model that will complete your prompt.

See models for additional details and options.

Required string length: 1 - 256
​
metadata
object
An object describing metadata about the request.


Show child attributes

​
stop_sequences
string[]
Custom text sequences that will cause the model to stop generating.

Our models will normally stop when they have naturally completed their turn, which will result in a response stop_reason of "end_turn".

If you want the model to stop generating when it encounters custom strings of text, you can use the stop_sequences parameter. If the model encounters one of the custom sequences, the response stop_reason value will be "stop_sequence" and the response stop_sequence value will contain the matched stop sequence.

​
stream
boolean
Whether to incrementally stream the response using server-sent events.

See streaming for details.

​
system

string
System prompt.

A system prompt is a way of providing context and instructions to Claude, such as specifying a particular goal or role. See our guide to system prompts.

​
temperature
number
Amount of randomness injected into the response.

Defaults to 1.0. Ranges from 0.0 to 1.0. Use temperature closer to 0.0 for analytical / multiple choice, and closer to 1.0 for creative and generative tasks.

Note that even with temperature of 0.0, the results will not be fully deterministic.

Required range: 0 < x < 1
​
thinking
object
Configuration for enabling Claude's extended thinking.

When enabled, responses include thinking content blocks showing Claude's thinking process before the final answer. Requires a minimum budget of 1,024 tokens and counts towards your max_tokens limit.

See extended thinking for details.

Enabled
Disabled

Show child attributes

​
tool_choice
object
How the model should use the provided tools. The model can use a specific tool, any available tool, decide by itself, or not use tools at all.

Auto
Any
Tool
ToolChoiceNone

Show child attributes

​
tools
object[]
Definitions of tools that the model may use.

If you include tools in your API request, the model may return tool_use content blocks that represent the model's use of those tools. You can then run those tools using the tool input generated by the model and then optionally return results back to the model using tool_result content blocks.

Each tool definition includes:

name: Name of the tool.
description: Optional, but strongly-recommended description of the tool.
input_schema: JSON schema for the tool input shape that the model will produce in tool_use output content blocks.
For example, if you defined tools as:

[
  {
    "name": "get_stock_price",
    "description": "Get the current stock price for a given ticker symbol.",
    "input_schema": {
      "type": "object",
      "properties": {
        "ticker": {
          "type": "string",
          "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
        }
      },
      "required": ["ticker"]
    }
  }
]
And then asked the model "What's the S&P 500 at today?", the model might produce tool_use content blocks in the response like this:

[
  {
    "type": "tool_use",
    "id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
    "name": "get_stock_price",
    "input": { "ticker": "^GSPC" }
  }
]
You might then run your get_stock_price tool with {"ticker": "^GSPC"} as an input, and return the following back to the model in a subsequent user message:

[
  {
    "type": "tool_result",
    "tool_use_id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
    "content": "259.75 USD"
  }
]
Tools can be used for workflows that include running client-side tools and functions, or more generally whenever you want the model to produce a particular JSON structure of output.

See our guide for more details.

Custom Tool
ComputerUseTool_20241022
BashTool_20241022
TextEditor_20241022
ComputerUseTool_20250124
BashTool_20250124
TextEditor_20250124

Show child attributes

​
top_k
integer
Only sample from the top K options for each subsequent token.

Used to remove "long tail" low probability responses. Learn more technical details here.

Recommended for advanced use cases only. You usually only need to use temperature.

Required range: x > 0
​
top_p
number
Use nucleus sampling.

In nucleus sampling, we compute the cumulative distribution over all the options for each subsequent token in decreasing probability order and cut it off once it reaches a particular probability specified by top_p. You should either alter temperature or top_p, but not both.

Recommended for advanced use cases only. You usually only need to use temperature.

Required range: 0 < x < 1
Response
200 - application/json
​
content
object[]
required
Content generated by the model.

This is an array of content blocks, each of which has a type that determines its shape.

Example:

[{"type": "text", "text": "Hi, I'm Claude."}]
If the request input messages ended with an assistant turn, then the response content will continue directly from that last turn. You can use this to constrain the model's output.

For example, if the input messages were:

[
  {"role": "user", "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"},
  {"role": "assistant", "content": "The best answer is ("}
]
Then the response content might be:

[{"type": "text", "text": "B)"}]
Text
Tool Use
Thinking
Redacted Thinking

Show child attributes

​
id
string
required
Unique object identifier.

The format and length of IDs may change over time.

​
model
string
required
The model that handled the request.

Required string length: 1 - 256
​
role
enum<string>
default:
assistant
required
Conversational role of the generated message.

This will always be "assistant".

Available options: assistant 
​
stop_reason
enum<string> | null
required
The reason that we stopped.

This may be one the following values:

"end_turn": the model reached a natural stopping point
"max_tokens": we exceeded the requested max_tokens or the model's maximum
"stop_sequence": one of your provided custom stop_sequences was generated
"tool_use": the model invoked one or more tools
In non-streaming mode this value is always non-null. In streaming mode, it is null in the message_start event and non-null otherwise.

Available options: end_turn, max_tokens, stop_sequence, tool_use 
​
stop_sequence
string | null
required
Which custom stop sequence was generated, if any.

This value will be a non-null string if one of your custom stop sequences was generated.

​
type
enum<string>
default:
message
required
Object type.

For Messages, this is always "message".

Available options: message 
​
usage
object
required
Billing and rate-limit usage.

Anthropic's API bills and rate-limits by token counts, as tokens represent the underlying cost to our systems.

Under the hood, the API transforms requests into a format suitable for the model. The model's output then goes through a parsing stage before becoming an API response. As a result, the token counts in usage will not match one-to-one with the exact visible content of an API request or response.

For example, output_tokens will be non-zero, even for an empty string response from Claude.

Total input tokens in a request is the summation of input_tokens, cache_creation_input_tokens, and cache_read_input_tokens.