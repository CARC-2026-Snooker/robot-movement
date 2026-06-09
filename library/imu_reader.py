"""
imu_reader.py — Stable MPU6050 reader for the CARC 2026 snooker robot.

Design priorities (in order):
  1. Never crash or lock the I2C bus
  2. Detect STILL vs MOVING quickly and accurately
  3. Provide gyro Z for heading integration

Mounted upside-down on this robot → gyro Z is negated.

Root cause of previous I2C lockups:
  - mpu6050() constructor initialises the chip; reading before it finishes
    causes Errno 121 (Remote I/O error), which can lock the SDA line.
  - Solution: wait 0.8s after construction before the first read.
  - On any read error: stop touching the bus for 2s, then recreate the
    sensor object completely (this resets the chip's I2C state machine).
  - Never read faster than once per 20ms (50Hz max).

Usage:
    imu = ImuReader()
    imu.start()           # non-blocking; calibrates in background (~3s)
    ...
    snap = imu.snapshot() # always safe to call; is_ready=False until calibrated
    imu.stop()
"""

import math, time, threading
from collections import deque
from config import DISABLE_IMU

try:
    from mpu6050 import mpu6050 as _MPU
    _HAS_HW = True
except ImportError:
    _HAS_HW = False

# ── Constants ────────────────────────────────────────────────────────────────
I2C_ADDR         = 0x68
UPSIDE_DOWN      = True      # negate gyro Z for upside-down mounting
LOOP_HZ          = 20        # read rate — 30Hz is plenty, less bus stress than 50Hz
CALIB_SAMPLES    = 90        # ~3s of samples for gyro bias
ACCEL_WINDOW     = 6         # rolling window for accel std
# BOOT_DELAY       = 0.8       # seconds to wait after mpu6050() before first read
BOOT_DELAY       = 1.5       # seconds to wait after mpu6050() before first read
ERROR_COOLDOWN   = 2.0       # seconds to wait after any I/O error
# MIN_READ_GAP     = 0.018     # seconds — never read faster than this
# MIN_READ_GAP     = 0.03     # seconds — never read faster than this
# MIN_READ_GAP     = 0.05     # seconds — never read faster than this
MIN_READ_GAP     = 0.075     # seconds — never read faster than this

# Activity thresholds
MOTION_START = 1.5   # motion definitely started
MOTION_STOP  = 0.3   # motion definitely stopped

# How long activity must stay quiet
STILL_HOLD_TIME = 0.20

class ImuReader:
    def __init__(self, addr: int = I2C_ADDR):
        self._addr    = addr
        self._lock    = threading.Lock()
        self._running = False
        self._thread  = None
        self._sensor  = None
        self._last_t  = 0.0
        self._history = deque(maxlen=ACCEL_WINDOW)

        # Public (read under lock via snapshot())
        self._gz      = 0.0
        self._hdg     = 0.0
        self._mag     = 1.0
        self._moving  = False
        self._ready   = False
        self._bias = 0.0
        self._bias_calibrated = False

        self._last_motion_time = time.time()

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self):
        """Start background thread immediately (non-blocking)."""
        if DISABLE_IMU:
            print("[IMU] Disabled - running without IMU.")
            return
        if not _HAS_HW:
            print("[IMU] No hardware found — running without IMU.")
            return
        self._running = True
        self._thread  = threading.Thread(target=self._run, daemon=True, name="imu")
        self._thread.start()
        print("[IMU] Thread started — calibrating in background...")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3.0)

    def reset_heading(self, val: float = 0.0):
        with self._lock:
            self._hdg = val % 360

    def snapshot(self) -> dict:
        """Always safe to call from any thread."""
        with self._lock:
            return {
                "is_ready":   self._ready,
                "is_moving":  self._moving,
                "gyro_z":     self._gz,
                "heading":    self._hdg,
                "accel_mag":  self._mag,
            }

    # ── Internal ──────────────────────────────────────────────────────────────

    def _init_sensor(self) -> bool:
        """Create sensor object + boot delay. Returns True on success."""
        try:
            self._sensor = _MPU(self._addr)
            time.sleep(BOOT_DELAY)          # chip needs time to finish booting
            return True
        except Exception as e:
            print(f"[IMU] init failed: {e}")
            self._sensor = None
            return False

    def _read(self):
        """One safe read. Enforces minimum inter-read gap. Raises on error."""
        gap = time.time() - self._last_t
        if gap < MIN_READ_GAP:
            time.sleep(MIN_READ_GAP - gap)
        a = self._sensor.get_accel_data()
        g = self._sensor.get_gyro_data()
        self._last_t = time.time()
        return a, g

    def _calibrate(self) -> bool:
        """Collect gyro bias. Returns True on success, False on any error."""
        samples = []
        dt = 1.0 / LOOP_HZ
        for _ in range(CALIB_SAMPLES):
            if not self._running:
                return False
            try:
                _, g = self._read()
                samples.append(g["z"])
            except Exception as e:
                print(f"[IMU] calibration error: {e}")
                return False
            time.sleep(dt)
        self._bias = sum(samples) / len(samples)
        return True

    def _run(self):
        dt = 1.0 / LOOP_HZ

        while self._running:

            # ── Step 1: initialise hardware ───────────────────────────────
            print("[IMU] Initialising sensor...")
            if not self._init_sensor():
                time.sleep(ERROR_COOLDOWN)
                continue

            # ── Step 2: calibrate gyro bias (ONLY ONCE) ───────────────────
            with self._lock:
                self._ready = False

            if not self._bias_calibrated:
                print("[IMU] Calibrating gyro bias...")
                if not self._calibrate():
                    print("[IMU] Calibration failed — cooling down...")
                    self._sensor = None
                    time.sleep(ERROR_COOLDOWN)
                    continue

                self._bias_calibrated = True
                self._last_motion_time = time.time()
                print(f"[IMU] Ready. Gyro bias = {self._bias:.3f} deg/s")
            else:
                print(f"[IMU] Reusing gyro bias = {self._bias:.3f} deg/s")

            with self._lock:
                self._ready = True

            # ── Step 3: normal read loop ──────────────────────────────────
            while self._running:
                t0 = time.time()
                try:
                    a, g = self._read()
                except Exception as e:
                    print(f"[IMU] read error: {e} — cooling down {ERROR_COOLDOWN}s")
                    with self._lock:
                        self._ready = False
                    self._sensor = None
                    time.sleep(ERROR_COOLDOWN)
                    break   # go back to init

                # Gyro Z (corrected for upside-down mounting)
                raw_gz = g["z"] - self._bias
                gz = -raw_gz if UPSIDE_DOWN else raw_gz

                # Accel magnitude → STILL/MOVING
                ax, ay, az = a["x"], a["y"], a["z"]
                mag = math.sqrt(ax*ax + ay*ay + az*az)
                self._history.append(mag)
                vals = list(self._history)
                mean = sum(vals) / len(vals)
                std  = math.sqrt(sum((v-mean)**2 for v in vals) / len(vals))
                activity = std

                now = time.time()

                if activity >= MOTION_START:
                    self._last_motion_time = now
                    moving = True

                elif activity >= MOTION_STOP:
                    self._last_motion_time = now
                    moving = self._moving

                else:
                    moving = (now - self._last_motion_time) < STILL_HOLD_TIME

                actual_dt = time.time() - t0
                with self._lock:
                    self._gz     = gz
                    self._hdg    = (self._hdg + gz * actual_dt) % 360
                    self._mag    = mag
                    self._moving = moving

                time.sleep(max(0.0, dt - (time.time() - t0)))