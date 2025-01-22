#!/usr/bin/env python3
import argparse
import asyncio
import logging
from functools import partial

from wyoming.info import AsrModel, AsrProgram, Attribution, Info
from wyoming.server import AsyncServer

from . import __version__
from .handler import LocalGSTTEventHandler

_LOGGER = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        required=True,
        help="Path to directory with local google stt"
    )
    parser.add_argument(
        "--uri",
        default="tcp://0.0.0.0:15770",
        help="unix:// or tcp://"
    )
    parser.add_argument(
        "--language",
        default="en-US",
        help="Default language to set for transcription",
    )

    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")

    parser.add_argument(
        "--log-format", default=logging.BASIC_FORMAT, help="Format for log messages"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print version and exit",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO, format=args.log_format
    )
    _LOGGER.debug(args)

    wyoming_info = Info(
        asr=[
            AsrProgram(
                name="Local Google STT " + args.language,
                description="Local Google STT " + args.language,
                attribution=Attribution(
                    name="loRe",
                    url="",
                ),
                installed=True,
                version=__version__,
                models=[
                    AsrModel(
                        name="Local Google STT Model",
                        description="Local Google STT Model",
                        attribution=Attribution(
                            name="google",
                            url="",
                        ),
                        installed=True,
                        # languages=['en-US', 'zh-CN'],
                        languages=[args.language],
                        version="1.0",
                    )
                ],
            )
        ],
    )

    server = AsyncServer.from_uri(args.uri)
    _LOGGER.info("Ready")

    model_lock = asyncio.Lock()

    await server.run(
        partial(
            LocalGSTTEventHandler,
            wyoming_info,
            args,
            model_lock,
        )
    )


# -----------------------------------------------------------------------------

def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
