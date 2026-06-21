# candle-usb

Python CAN / CAN FD driver for [candleLight](https://github.com/candle-usb/candleLight_fw) USB adapters and Geschwister Schneider gs_usb devices — Windows, Linux, macOS.

## Install

```
pip install candle-usb
```

Requires [libusb](https://libusb.info). On Linux install `libusb-1.0-0` and add a udev rule; on Windows use [Zadig](https://zadig.akeo.ie) to bind WinUSB to the device.

## Compatible firmware

This library works with any adapter running the gs_usb USB protocol:

- **[CANnectivity](https://github.com/CANnectivity/cannectivity)** — open-source Zephyr-based firmware for CAN / CAN FD adapters. Recommended for CAN FD support.
- **[candleLight](https://github.com/candle-usb/candleLight_fw)** — popular STM32-based firmware for classic CAN adapters (CANable, canable-pro, etc.)

For CAN FD (`--data-bitrate`) the adapter must run CANnectivity or another gs_usb firmware with FD capability.

## pycandump

A `candump`-style live monitor is included and available on the PATH after install:

```
pycandump                                      # classic CAN, 500 kbps, listen-only
pycandump --bitrate 250000
pycandump --data-bitrate 1000000               # enables CAN FD mode
pycandump --active                             # required when adapter is sole receiver
pycandump --filter 0x100:0x7FF
pycandump --fd-only
pycandump --log trace.log
pycandump --device 6:14                        # pick a specific USB device
```

> **Note on `--active`:** in listen-only mode the adapter sends no ACK bits. If it is
> the only receiver on the bus the sender will retransmit the same frame indefinitely.
> Pass `--active` whenever you are the sole node.

## API usage

### Classic CAN

```python
from candle_usb.gs_usb import GsUsb
from candle_usb.gs_usb_frame import GsUsbFrame
from candle_usb.constants import CAN_EFF_FLAG

devs = GsUsb.scan()
dev  = devs[0]

dev.set_bitrate(500000)
dev.start()

frame = GsUsbFrame(can_id=0x7FF, data=b"\x01\x02\x03")
dev.send(frame)

rx = GsUsbFrame()
if dev.read(rx, timeout_ms=100):
    print(rx)

dev.stop()
```

### CAN FD

```python
from candle_usb.gs_usb import GsUsb
from candle_usb.gs_usb_frame import GsUsbFrame
from candle_usb.constants import (
    GS_CAN_MODE_FD, GS_CAN_MODE_HW_TIMESTAMP,
    GS_CAN_FEATURE_FD, GS_CAN_FEATURE_HW_TIMESTAMP,
)

dev = GsUsb.scan()[0]
dev.set_bitrate(250000)
dev.set_data_bitrate(1000000)
dev.start(GS_CAN_MODE_FD | GS_CAN_MODE_HW_TIMESTAMP)

frame = GsUsbFrame()
if dev.read(frame, timeout_ms=200):
    print(frame)          # shows FD / BRS / ESI flags automatically

dev.stop()
```

## Publishing a new release

Push a version tag and GitHub Actions builds and publishes to PyPI automatically:

```
git tag v0.4.0
git push origin v0.4.0
```

The workflow uses [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC — no API token needed). On first use, configure the publisher on PyPI under the project settings:
- Publisher: GitHub Actions
- Owner: `diegoasanza`
- Repository: `candle-usb`
- Workflow: `publish.yml`
- Environment: `pypi`

## Fork notice

This is a fork of [gs_usb](https://github.com/jxltom/gs_usb) by jxltom, extended with:

- Correct CAN FD frame parsing — dispatch on `GS_CAN_FLAG_FD` in the frame header (matching the Linux kernel driver) instead of packet size, which breaks when `GS_CAN_MODE_PAD_PKTS_TO_MAX_PKT_SIZE` is active
- Hardware timestamp support (`GS_CAN_MODE_HW_TIMESTAMP`)
- `set_data_bitrate()` and full CAN FD mode setup
- `pycandump` CLI monitor
- Identify LED and bus termination control

## License

MIT — see [LICENSE](LICENSE).  
Original work © 2020 jxltom. Modifications © 2026 Diego Asanza.
