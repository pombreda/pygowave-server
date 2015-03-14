# PyGoWave Server Roadmap #

The up-to-date todo list can be viewed at the Issues tab.

## Alpha 0.1 ##
_Quick-and-dirty Gadget wrapper_
  * Create data models for basic server operation - done
  * Think of an event sending/dispatching engine - done
  * Experiment with robot client libraries - done
  * Find appropriate tools - done
  * Create a basic design for webpages - done
  * Implement registration form for PyGoWave - done
  * Create a basic settings page - done
  * Add a Gadget registration form - done
  * Add a Wave creation form - done
  * Build a small Wave Gadget environment emulator - done
  * Implement simple client script for Gadget communication - done

## Alpha 0.2 ##
_Bugfixed alpha release_
  * Fix upcoming bugs

## Alpha 0.3 ##
_Improved PyGoWave client, basic Wave communication working_
  * Look for a better JavaScript toolkit - done
  * Port existing non-client code to the new toolkit - done
  * Read and understand Operational Transformation - done
  * Design and implement a client object model
  * Implement RPC server back-end for the client object model

## Alpha 0.4 ##
_Robot support, bugfixed Wave communication_
  * Implement a serialization for the server Wave model
  * Add a Robots tab and create a Robot registration form
  * Implement an event handler for robots into the RPC server
  * Try to run an example robot with the server via the Google App Engine
  * Decouple the Robot API from the Google App Engine to allow non-GAE Robots on Django

## Beta 0.5 ##
_Ready for daily use, Embed API ready_

## Beta 0.6 ##
_Bugfixes, advanced Wave communication_
  * Implement playback feature

## Beta 0.7 ##
_Federation Protocol implemented_
  * Implement Google Wave Federation Protocol

## Beta 0.8 ##
_More bugfixes_

## Beta 0.9 ##
_Last beta release_
  * Use distutils (and others) to create an installable version

## Release 1.0 ##
_Production-ready system_