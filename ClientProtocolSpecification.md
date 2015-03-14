# Introduction #

PyGoWave Server uses a proprietary (i.e. non-standard, but well, there is no standard) protocol to communicate to its web client interface, just like Google use their proprietary protobuf-based client protocol for the officially released console client. It is roughly based on the Wave Robot API.

This document aims to give an overview how the protocol is structured.

# Messages #

All messages are serialized via JSON and have at least a "type" field. Depending on type they also may have a "property" field. While "type" is strictly a string, "property" can be of any type. It may be an integer, a string or even a hash map as long as it's serializable via JSON; the contents of "property" is defined by the type of the message.

Messages may also have a direction, where the client-to-server message has different contents than the server-to-client message.

Note: Not all messages are subject to Operational Transformation and there are some messages that do not modify any data on the server but are simply for obtaining data from the server.

## Synchronous messages ##

These messages are request-response based and thus the client has to wait for the server to answer or take action.

### WAVELET\_OPEN ###

#### Client -> Server ####
Property:
```
(none)
```
Description:
> Sent by the client to request initial Wavelet data and to start receiving messages for that Wavelet. The Wavelet ID is retrieved internally from the message broker.

#### Server -> Client ####
Property:
```
{
    "wavelet": {
        "rootBlipId": (string),
        "title": (string),
        "creator": (string),
        "creationTime": (int),
        "dataDocuments": None,
        "waveletId": (string),
        "participants": [(string), ...],
        "version": (int),
        "lastModifiedTime": (int),
        "waveId": (string)
    },
    "blips": {
        (string): {
            "blipId": (string),
            "content": (string),
            "elements": [
                {
                    "index": (int),
                    "type": (string),
                    "properties": (obj)
                },
                ...
            ],
            "contributors": [(string), ...],
            "creator": (string),
            "parentBlipId": (string),
            "annotations": [
                {
                    "range": {
                        "start": (int),
                        "end": (int)
                    },
                    "name": (string),
                    "value": (obj)
                },
                ...
            ],
            "waveletId": (string),
            "version": (int),
            "lastModifiedTime": (int),
            "childBlipIds": [(string), ...],
            "waveId": (string),
            "submitted": (boolean)
            "checksum": (string)
        },
        ...
    }
}
```
Description:
> Contains the Wavelet and its blips in serialized form.

### PARTICIPANT\_INFO ###

#### Client -> Server ####

Property:
```
[
    (string),
    ...
]
```
Description:
> Requests information on one or more participants (by id).

#### Server -> Client ####

Property:
```
[
    {
        "id": (string),
        "displayName": (string),
        "thumbnailUrl": (string),
        "profileUrl": (string),
        "isBot": (boolean)
    },
    ...
]
```
Description:
> The resulting participant information.

### PARTICIPANT\_SEARCH ###

#### Client -> Server ####

Property:
```
(string)
```
Description:
> Searches for participants. Property is the search query.

#### Server -> Client ####

Property:
```
    "result": (string),
    "data": [(string), ...]
```
Description:
> Results of a participant serach. If "result" is "OK", then data is a list of matching participant IDs. If result is "TOO\_SHORT", then data is an integer of the minimum required length.

### GADGET\_LIST ###

#### Client -> Server ####

Property:
```
(none)
```
Description:
> Requests a list of all available gadgets.

#### Server -> Client ####

Property:
```
[
    {
        "id": (int),
        "uploaded_by": (string),
        "name": (string),
        "descr": (string),
        "url": (string)
    },
    ...
]
```
Description:
> The requested list of participants. "uploaded\_by" is the uploader's participant name.

### WAVELET\_ADD\_PARTICIPANT ###

#### Client -> Server ####

Property:
```
(string)
```
Description:
> Adds a participant to the Wavelet. The property is the participant's ID.

#### Server -> Client ####

Property:
```
(string)
```
Description:
> Broadcast message of a newly added participant. The property is the participant's ID.

### WAVELET\_REMOVE\_SELF ###

#### Client -> Server ####

Property:
```
(none)
```
Description:
> Requests to remove the connected participant from the wave.

#### Server -> Client ####

Property:
```
(none)
```
Description:
> Acknowledges removal of the connected participant from the wave.

## OT messages ##

All messages which are subject to Operational Transformation are contained in an
OPERATION\_MESSAGE\_BUNDLE message. The server responds with a OPERATION\_MESSAGE\_BUNDLE\_ACK message afterwards and sends a OPERATION\_MESSAGE\_BUNDLE message to each other connected client.

### OPERATION\_MESSAGE\_BUNDLE ###

#### Client -> Server ####

Property:
```
{
    "version": (int),
    "operations": [(obj), ...]
}
```
Description:
> Operations sent by the client.

#### Server -> Client ####

Property:
```
{
    "version": (int),
    "operations": [(obj), ...],
    "blipsums": {
        (string): (string),
        ...
    }
}
```
Description:
> Operations sent by the server. There is an additional "blipsums" field that contains a hash map "blipId: sha1(blipText)".

### OPERATION\_MESSAGE\_BUNDLE\_ACK ###

#### Server -> Client only ####

Property:
```
{
    "version": (int),
    "blipsums": {
        (string): (string),
        ...
    }
}
```
Description:
> Send when the server acknowledges a client's message bundle.

## Serialized Operations ##

All operations have the following fields:

```
{
    "type": (string),
    "wave_id": (string),
    "wavelet_id": (string),
    "blip_id": (string),
    "index": (int),
    "property": (obj),
}
```

Where property again is a custom object depending on the type.

The following operations are implemented:

### DOCUMENT\_INSERT ###

Property:
```
(string)
```
Description:
> Insert text into the blip. Property is the text.

### DOCUMENT\_DELETE ###

Property:
```
(int)
```
Description:
> Delete text from the blip. Property is the length.

### DOCUMENT\_ELEMENT\_INSERT ###

Property:
```
{
    "type": (string),
    "properties": (obj)
}
```
Description:
> Insert an element into the blip.

### DOCUMENT\_ELEMENT\_DELETE ###

Property:
```
(none)
```
Description:
> Delete an element from the blip.

### DOCUMENT\_ELEMENT\_DELTA ###

Property:
```
{
    (string): (string),
    ...
}
```
Description:
> Apply a delta to the element's state object on the blip.

### DOCUMENT\_ELEMENT\_SETPREF ###

Property:
```
{
    "key": (string),
    "value": (string)
}
```
Description:
> Set a UserPref of the element on the blip.

# Examples #

Here are some message dumps for you to see the protocol in action:

```
-- Client -> Server --
{
    'type': 'WAVELET_OPEN'
}

-- Server -> Client --
{
    'type': 'WAVELET_OPEN',
    'property': {
        'wavelet': {
            'waveletId': 'otdWRSQCcs!conv+root',
            'participants': ['opera@localhost'],
            'version': 0,
            'rootBlipId': 'eUFnen1V90',
            'title': 'Demo',
            'lastModifiedTime': 1251282070000,
            'creator': 'opera@localhost',
            'creationTime': 1251282070000,
            'waveId': 'otdWRSQCcs',
            'dataDocuments': None
        },
        'blips': {
            'eUFnen1V90': {
                'blipId': 'eUFnen1V90',
                'elements': [],
                'contributors': [],
                'creator': 'opera@localhost',
                'lastModifiedTime': 1251282070000,
                'waveId': 'otdWRSQCcs',
                'waveletId': 'otdWRSQCcs!conv+root',
                'checksum': 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
                'parentBlipId': None,
                'submitted': False,
                'content': '',
                'version': 0,
                'childBlipIds': [],
                'annotations': []
            }
        }
    },
}

-- Client -> Server --
{
    'type': 'PARTICIPANT_INFO',
    'property': ['opera@localhost']
}

-- Server -> Client --
{
    'type': 'PARTICIPANT_INFO',
    'property': {
        'opera@localhost': {
            'profileUrl': '',
            'isBot': 0,
            'thumbnailUrl': '/pygowave/media/avatars/f526_Knuckles.png',
            'displayName': 'opera',
            'id': 'opera@localhost'
        }
    }
}

-- Client -> Server --
{
    'type': 'OPERATION_MESSAGE_BUNDLE',
    'property': {
        'operations': [
            {
                'type': 'DOCUMENT_INSERT',
                'index': 0,
                'blip_id': 'eUFnen1V90',
                'wavelet_id': 'otdWRSQCcs!conv+root',
                'wave_id': 'otdWRSQCcs',
                'property': 'X'
            }
        ],
        'version': 0
    }
}

-- Server -> Client --
{
    'type': 'OPERATION_MESSAGE_BUNDLE_ACK',
    'property': {
        'blipsums': {
            'eUFnen1V90': 'c032adc1ff629c9b66f22749ad667e6beadf144b'
        },
        'version': 1
    }
}

-- Broadcast --
{
    'type': 'OPERATION_MESSAGE_BUNDLE',
    'property': {
        'operations': [
            {
                'type': 'DOCUMENT_INSERT',
                'index': 0,
                'blip_id': 'eUFnen1V90',
                'wavelet_id': 'otdWRSQCcs!conv+root',
                'wave_id': 'otdWRSQCcs',
                'property': 'X'
            }
        ],
        'blipsums': {
            'eUFnen1V90': 'c032adc1ff629c9b66f22749ad667e6beadf144b'
        },
        'version': 1
    }
}

-- Client -> Server --
{
    'type': 'OPERATION_MESSAGE_BUNDLE',
    'property': {
        'operations': [
            {
                'type': 'DOCUMENT_DELETE',
                'index': 0,
                'blip_id': 'eUFnen1V90',
                'wavelet_id': 'otdWRSQCcs!conv+root',
                'wave_id': 'otdWRSQCcs',
                'property': 1
            }
        ],
        'version': 1
    }
}

-- Server -> Client --
{
    'type': 'OPERATION_MESSAGE_BUNDLE_ACK',
    'property': {
        'blipsums': {
            'eUFnen1V90': 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
        },
        'version': 2
    }
}

-- Broadcast --
{
    'type': 'OPERATION_MESSAGE_BUNDLE',
    'property': {
        'operations': [
            {
                'type': 'DOCUMENT_DELETE',
                'index': 0,
                'blip_id': 'eUFnen1V90',
                'wavelet_id': 'otdWRSQCcs!conv+root',
                'wave_id': 'otdWRSQCcs',
                'property': 1
            }
        ],
        'blipsums': {
            'eUFnen1V90': 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
        },
        'version': 2
    }
}

-- Client -> Server --
{
    'type': 'GADGET_LIST'
}

-- Server -> Client --
{
    'type': 'GADGET_LIST',
    'property': [
        {
            'id': 5,
            'url': 'http://svg-edit.googlecode.com/svn/trunk/wave/svg-edit.xml',
            'descr': 'SVG editor (svn version)',
            'name': 'SVG-edit',
            'uploaded_by': 'p2k'
        },
        {
            'id': 3,
            'url': 'http://blah.appspot.com/wave/sudoku/sudoku.xml',
            'descr': 'Sudoku Gadget (by Google).',
            'name': 'Austin Test',
            'uploaded_by': 'p2k'
        },
        {
            'id': 4,
            'url': 'http://wave.thewe.net/gadgets/todo/todo.xml',
            'descr': 'Todo list by avital.',
            'name': 'Reorderable to-do list',
            'uploaded_by': 'p2k'
        }
    ]
}

-- Client -> Server --
{
    'type': 'PARTICIPANT_SEARCH',
    'property': 'sa'
}

-- Server -> Client --
{
    'type': 'PARTICIPANT_SEARCH',
    'property': {
        'result': 'TOO_SHORT',
        'data': 3
    }
}

-- Client -> Server --
{
    'type': 'PARTICIPANT_SEARCH',
    'property': 'saf'
}

-- Server -> Client --
{
    'type': 'PARTICIPANT_SEARCH',
    'property': {
        'result': 'OK',
        'data': ['safari@localhost']
    }
}

-- Client -> Server --
{
    'type': 'WAVELET_ADD_PARTICIPANT',
    'property': 'safari@localhost'
}

-- Broadcast --
{
    'type': 'WAVELET_ADD_PARTICIPANT',
    'property': 'safari@localhost'
}
```