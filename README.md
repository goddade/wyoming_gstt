# Wyoming Gasr

[Wyoming protocol](https://github.com/rhasspy/wyoming) server for the [gasr](https://github.com/biemster/gasr).

Setup
---
```
git clone https://github.com/goddade/wyoming_gstt
cd wyoming_gstt
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```
Start the STT service:
---
```
source .venv/bin/activate
python3 -m wyoming_gstt --data-dir PATH_TO_DATA --language en-US --uri 'tcp://127.0.0.1:15000'
```
Change `PATH_TO_DATA` to the directory containing `libsoda.so` and recognition data, for example:
```
$ ls PATH_TO_DATA
en-US  libsoda.so  zh-CN
$ ls PATH_TO_DATA/en-US/
acousticmodel     denorm         g2p_phonemes.syms  metadata                  semantics.pumpkin
config.pumpkin    diarization    g2p.syms           monastery_config.pumpkin  SODA_punctuation_config.pb
configs           endtoendmodel  langid             offline_action_data.pb    SODA_punctuation_model.tflite
context_prebuilt  g2p            magic_mic          pumpkin.mmap              voice_match
```

Homeassistant configuration
---
Install the [Wyoming Protocol](https://www.home-assistant.io/integrations/wyoming#configuration) Add-On. 

Select the Wyoming Protocol, select the Add Service button, enter the address and port of the gasr service.

Select Local Google STT in the Assist configuration.

Tested
---

google stt version: libsoda.so.1.1.1.7

stt data version:
    cmn-Hans-CN: SODAModels.1.3054.0
    en-US: SODAModels.1.3050.0

protobuf version: 3.20.3



