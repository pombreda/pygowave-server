# Introduction #

(This page is still unfinished)

We all know Google has its own Gadget RPC framework to allow IFrame-to-IFrame and IFrame-to-Parent communication. Besides that it is closed-source, it does not allow cross-domain communication.

This document describes an open cross-domain approach of that kind of communication.

# How it works #

The Gadget RPC framework script spawns two hidden IFrames. One is called the Broker and the other one is called the Delegate.

## The Broker ##

  * Resides on a common domain for all IFrames (and the top window)
  * Accepts calls via its URL's fragment identifier
  * Knows the URL of the sibling Delegate
  * Forwards calls to another Broker e.g. the top window's Broker or a sibling's Broker. The message is queued here (not implemented yet)

## The Delegate ##

  * Resides on the IFrame's domain so it can communicate directly with the underlying RPC framework (which in turn calls the IFrame's registered callbacks)
  * Also accepts calls via its URL's fragment identifier, this is always done by the Broker
  * Delivers the message to the RPC framework

## Some notes ##

  * This does not break any security. Each party must provide their own Delegates; no Delegate, no access.
  * The fragment identifier "hack" is used to prevent the hidden IFrames from reloading
  * The tradeoff: Detecting a change of the fragment identifier requires polling
  * To make all IFrames use the same Broker URL and keeping track of who-is-who, the URL and an unique ID is passed to each IFrame (there is a function to do that conveniently)
  * To pass around data, JSON and Base64 is used internally
  * This framework may get obsoleted by HTML 5

# How to use #

  * Include the gadgets-rpc.js script in your top window and gadgets
  * Get a copy of broker.html and delegate.html and install it on your server; make sure that the latter is on a path of the target frames URL (includes subdomain, domain and path)
  * Call gadgets.rpc.init(delegateURL) on page load
  * Use gadgets.rpc.setupGadget(url, domElement) to setup an IFrame (passes Broker URL and the name-property of the element)
  * For all other calls, see Google's Gadget RPC API