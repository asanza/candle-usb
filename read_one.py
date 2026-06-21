#!/usr/bin/env python3
"""Read 5 current CAN FD frames.

The CANnectivity firmware blocks between frames (semaphore pattern).
One reader thread always has a gap between reads — firmware backs up.
Fix: N concurrent reader threads so there is always an outstanding
libusb_bulk_transfer when one completes, mirroring the kernel's
GS_MAX_RX_URBS approach.
"""
import queue
import threading
from struct import unpack

from candle_usb.gs_usb import GsUsb
from candle_usb.gs_usb_frame import GsUsbFrame, GS_USB_FRAME_SIZE_FD_HW_TIMESTAMP
from candle_usb.constants import (
    GS_CAN_MODE_HW_TIMESTAMP, GS_CAN_MODE_FD,
    GS_CAN_FEATURE_FD, GS_CAN_FEATURE_HW_TIMESTAMP, CAN_ERR_FLAG,
)

_BREQ_TIMESTAMP = 0x06
NUM_READERS     = 8   # concurrent outstanding bulk reads

devs = GsUsb.scan()
if not devs:
    print("No device found")
    exit(1)

dev = devs[0]
print("Device:", dev)

cap = dev.device_capability
print("Feature flags : 0x{:04X}  FD={}  HW_TS={}".format(
    cap.feature,
    bool(cap.feature & GS_CAN_FEATURE_FD),
    bool(cap.feature & GS_CAN_FEATURE_HW_TIMESTAMP),
))
print("Clock         : {} MHz".format(cap.fclk_can // 1_000_000))

dev.reset()
dev.stop()

ok_nom  = dev.set_bitrate(250000)
ok_data = dev.set_data_bitrate(1000000)
print("set_bitrate(250000)        ->", "OK" if ok_nom  else "FAILED")
print("set_data_bitrate(1000000)  ->", "OK" if ok_data else "FAILED")

flags =  GS_CAN_MODE_HW_TIMESTAMP | GS_CAN_MODE_FD
dev.start(flags)

hw_ts = bool(dev.device_flags & GS_CAN_MODE_HW_TIMESTAMP)
print("device_flags               : 0x{:04X}  HW_TS={}".format(dev.device_flags, hw_ts))

# N concurrent reader threads — each blocks in libusb_bulk_transfer.
# When firmware unblocks one, another is already waiting → no gap.
raw_q = queue.Queue()
_stop = threading.Event()

def _reader():
    while not _stop.is_set():
        try:
            data = dev.gs_usb.read(0x81, GS_USB_FRAME_SIZE_FD_HW_TIMESTAMP, 500)
            raw_q.put(bytes(data))
        except Exception:
            pass

for _ in range(NUM_READERS):
    threading.Thread(target=_reader, daemon=True).start()

# Reference timestamp: skip frames that pre-date this session.
ref_ts = None
if hw_ts:
    try:
        raw = dev.gs_usb.ctrl_transfer(0xC1, _BREQ_TIMESTAMP, 0, 0, 4)
        ref_ts = unpack("<I", bytes(raw))[0]
        print("Reference timestamp        : {} us".format(ref_ts))
    except Exception as e:
        print("BREQ_TIMESTAMP failed ({}) — no staleness filter".format(e))

print()

frame   = GsUsbFrame()
shown   = 0
skipped = 0

while shown < 5:
    try:
        data = raw_q.get(timeout=2.0)
    except queue.Empty:
        print("  (timeout)")
        continue

    GsUsbFrame.unpack_into(frame, data, hw_ts)

    if frame.echo_id != 0xFFFFFFFF:
        continue
    if frame.can_id & CAN_ERR_FLAG:
        continue
    if ref_ts is not None and frame.timestamp_us < ref_ts:
        skipped += 1
        continue

    if skipped:
        print("(skipped {} stale)".format(skipped))
        skipped = 0

    print("RAW  : {}".format(" ".join("{:02X}".format(b) for b in data)))
    print("ts   : {} us".format(frame.timestamp_us))
    print("id   : 0x{:X}  ext={}".format(frame.arbitration_id, frame.is_extended_id))
    print("dlc  : {}  data_len={}".format(frame.can_dlc, frame.data_length))
    print("flags: 0x{:02X}  fd={}  brs={}  esi={}  ovfl={}".format(
        frame.flags, frame.is_fd, frame.is_bitrate_switch,
        frame.is_error_state_indicator, bool(frame.flags & 0x01)))
    print("data : {}".format(" ".join("{:02X}".format(b) for b in frame.data[:frame.data_length])))
    print()
    shown += 1

_stop.set()
dev.stop()
