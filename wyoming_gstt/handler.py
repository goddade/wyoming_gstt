"""Event handler for clients of the server."""
import argparse
import asyncio
import logging

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioStart, AudioChunk, AudioChunkConverter, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler

from soda_stt import SodaClient

_LOGGER = logging.getLogger(__name__)


class LocalGSTTEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    def __init__(
            self,
            wyoming_info: Info,
            cli_args: argparse.Namespace,
            model_lock: asyncio.Lock,
            *args,
            **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.model_lock = model_lock
        self.audio_converter = AudioChunkConverter(
            rate=16000,
            width=2,
            channels=1,
        )
        self.soda = SodaClient(self.cli_args.data_dir, self.cli_args.language, channel_count=1, sample_rate=16000)
        self.soda.create()

    async def handle_event(self, event: Event) -> bool:
        if AudioStart.is_type(event.type):
            _LOGGER.debug("Receiving audio")
            self.soda.begin()

        if AudioChunk.is_type(event.type):
            chunk = AudioChunk.from_event(event)
            chunk = self.audio_converter.convert(chunk)
            self.soda.add_audio(chunk.audio)

            return True

        if AudioStop.is_type(event.type):
            _LOGGER.debug("Audio stopped")
            text = self.soda.end()
            if text:
                text = text.strip()
                _LOGGER.info(text)
            else:
                text = ""

            await self.write_event(Transcript(text=text).event())
            _LOGGER.debug("Completed request")

            # Reset
            # self._language = self.cli_args.language

            return False

        if Transcribe.is_type(event.type):
            # transcribe = Transcribe.from_event(event)
            # if transcribe.language:
            #     if self.soda.language != transcribe.language:
            #         del self.soda
            #         self.soda = SodaClient(self.cli_args.data_dir, transcribe.language, channel_count=1,
            #                                sample_rate=16000)
            #         self.soda.create()
            #         _LOGGER.debug("Language set to %s", transcribe.language)
            return True

        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        return True
