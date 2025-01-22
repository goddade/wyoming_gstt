Wyoming warper for https://github.com/biemster/gasr
===

Tested:
---

google stt version: libsoda.so.1.1.1.7

stt data version:
    cmn-Hans-CN: SODAModels.1.3054.0
    en-US: SODAModels.1.3050.0

protobuf version: 3.20.3


Usage:
---
    python3 -m wyoming_gstt --data-dir PATH_TO_DATA --language en-US --uri 'tcp://127.0.0.1:15000'
