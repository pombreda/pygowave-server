# Introduction #

I decided to write a quick-and-dirty Google Wave Server which shall constantly evolve into full-featured production-ready software. This implies, that writing the server is an iterative process.

The tradeoff of trying to be as fast as possible is a certain tendency to, simply spoken, go the wrong way and maybe to reach dead ends in software engineering. So I sat down, took a breath and carefully thought up a plan.

# The Server Architecture #

After reading the API up and down and having taken a glimpse at the Federation Protocol specification I came to the following points (summed up pretty tight):

### From the Federation Protocol's View ###

  * A Wave is a container for Wavelets; it has at least one Wavelet which is the root Wavelet
  * Wavlets spawn by writing data to a theoretically existing Wavelet, it is created if it didn't exist before
  * A Wavelet is a standard XML document with some constraints; additionaly Wavelets have participants (with a set of permissions) and annotations (that handle styling)
  * There are no semantics in the Wavelet Document's content; things like Blips or Gadgets are simple XML tags like any other
  * A sophisticated technique is used to maintain mutations to the Wavelet - called "Deltas" and "Wavelet operations"
  * Data is exchanged through the (strictly) defined Federation Protocol

### From the Robot API's View ###

  * Everything is accessed through an object model; there is no XML document
  * The Wave only exists as an ID string; Robots cannot get access to a list of Wavelets on a Wave
  * A Wavelet is an Object that consists of participants, Data Documents and Blips
  * Blips have a hierarchy, they have contributors, a creator and a Document
  * The Document in a Blip has annotations, raw text, Gadgets and Form Elements
  * Mutations to the Wavelet are specified by Events from the server side and Operations from the client side
  * Data is exchanged through a proprietary protocol; at the time of writing this follows a request-response scheme with JSON-marshalled Java objects; there are no "Deltas" like in the Federation Protocol

### From the Google Wave Client's View ###

  * There is little information available on the Federation Protocol website. The client seems to receive a snapshot of the Wave on startup. Nothing explicit is stated here.

### From the Gadget API's View ###

  * A Gadget only maintains its own state and only gets a few hints what happens in the Wavelet
  * Its state is represented with a one-dimensional JavaScript map
  * Data is exchanged on behalf of the Google Gadgets API; it is obviously fed to the Google Wave Client
  * The Gadget does not modifiy its state by itself. It rather calls submitDelta() and lets the API do this.

# The Client Architecture #

See PyGoWaveClientArchitecture.

# How PyGoWave Server is implemented #
_My current approach, and why I went for it._

**Focus on the API's protocol**

> As long as there are no other Wave Servers and I am not able to communicate with Google's, I'll stick with the Robots, Gadgets and a rudimentary Wave client.

**Maintain the API's object model**

> This allows me to rapidly establish a working communication with Robots and Gadgets. For implementing the Federation Protocol it's quite a bit cumbersome.

**Create a Google Gadgets / Google Wave environment**

> Without access to the Google Wave Client I am foreced to build my own client too. This is a heavy task and will take a huge amount of time. Nevertheless, I'll do it.

> Gadgets are already running fine in my testing environment. The next step is their integration in a real Wave.

> Note: I dropped the term "emulation" here. This won't be an emulator anymore, it is the real thing! :D

**Choose Python**

> Platform independency, clearity, nice design of the language, the ease and speed of writing working programs and much more are my reasons for choosing Python. I could write a feature-length hymn for this language.

**Choose Django (and MooTools)**

> With Django, a persistent object model can be created in a few hours (as you have probably seen). Because of the request-response scheme of the Robot API there shouldn't be a problem to shove those events and context into a robot.

> I switched from jQuery to MooTools. Not only MooTools has everything that jQuery has, but it also provides a nice toolset for object oriented programming in JavaScript. The Gadget API wrapper is written in vanilla JavaScript so it won't interfere with any toolkit a Gadget may choose.

> Another reason for choosing Django: After all, you want to administer your Wave Server through some sort of Web Interface - Ok, a Wave and/or Gadget would do the trick too. At least something must serve those IFrames and JavaScripts...

**Choose Orbited and RabbitMQ**

> The current Gadget emulator and the upcoming Wave client doesn't use any (short-)polling. Instead, a Comet framework is in place for which I took Orbited (guessed right, it's written in Python). This reduces latency to about a quarter of a second which is sufficient for Waves.

> Because every data traffic in a Wave is sent via messages, a message broker had to be installed. I chose RabbitMQ over ActiveMQ because the former is written in Erlang, a nice functional language with built-in parallelism, and the latter is written in Java, which I avoid because of personal reasons.

> The main node of data exchange between client and server is represented in an AMQP RPC server (with AMQP being the main messaging protocol of RabbitMQ). This RPC server acts as a controller in terms of the MVC design pattern. Because of the architecture of the message broker, this server can be easily split into multiple threads which can handle Wave messages in parallel.

## What's with the Federation Protocol? ##

I think of emulating the XML Wavelet document with my object model. This requires some more thinking and even more work to be done, but will keep things straight for Robots and the client.

There is a module for connecting RabbitMQ and ejabberd, a Jabber server implementation. It may be possible to set something up that manages the Federation messages. I'll investigate this later.

# Conclusion #

So that's what already is and will become out of PyGoWave Server in the future. If you want to provide any feedback feel free to enter a comment on this wiki page.

I'm always open to suggestions on how to make this thing better.