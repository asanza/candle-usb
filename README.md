# candle-usb

Python CAN / CAN FD driver for [candleLight](https://github.com/candle-usb/candleLight_fw) USB adapters and Geschwister Schneider gs_usb devices — Windows, Linux, macOS.

## Install

```
pip install candle-usb
```

Requires [libusb](https://libusb.info). On Linux install `libusb-1.0-0` and add a udev rule; on Windows use [Zadig](https://zadig.akeo.ie) to bind WinUSB to the device.

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
from gs_usb.gs_usb import GsUsb
from gs_usb.gs_usb_frame import GsUsbFrame
from gs_usb.constants import CAN_EFF_FLAG

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
from gs_usb.gs_usb import GsUsb
from gs_usb.gs_usb_frame import GsUsbFrame
from gs_usb.constants import (
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

## Credits

Based on [gs_usb](https://github.com/jxltom/gs_usb) by jxltom. Extended with CAN FD support, correct flags-based frame parsing, hardware timestamp handling, and the `pycandump` CLI.

## License

MIT
