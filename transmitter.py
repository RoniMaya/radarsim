"""
Radar Transmitter Configuration and Waveform Modeling

This module provides the `Transmitter` class, which defines the parameters
and properties of a radar transmitter. It includes tools for configuring waveform
properties, pulse modulation, and transmitter channel settings. The module supports
advanced radar system simulations by enabling custom waveform generation and
transmitter channel modulation.

---

- Copyright (C) 2018 - PRESENT  radarsimx.com
- E-mail: info@radarsimx.com
- Website: https://radarsimx.com

::

    ██████╗  █████╗ ██████╗  █████╗ ██████╗ ███████╗██╗███╗   ███╗██╗  ██╗
    ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔════╝██║████╗ ████║╚██╗██╔╝
    ██████╔╝███████║██║  ██║███████║██████╔╝███████╗██║██╔████╔██║ ╚███╔╝
    ██╔══██╗██╔══██║██║  ██║██╔══██║██╔══██╗╚════██║██║██║╚██╔╝██║ ██╔██╗
    ██║  ██║██║  ██║██████╔╝██║  ██║██║  ██║███████║██║██║ ╚═╝ ██║██╔╝ ██╗
    ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝     ╚═╝╚═╝  ╚═╝

"""

from typing import List, Dict, Union, Optional
import numpy as np
from numpy.typing import NDArray


class Transmitter:
    """
    Defines the basic parameters and properties of a radar transmitter.

    This class handles the waveform configuration, pulse parameters,
    and properties of the transmitter channels.

    :param f: Waveform frequency in Hertz (Hz).
        The value can be:

        - A single number: For a single-tone waveform.
        - A list ``[f_start, f_stop]``: For linear frequency modulation.
        - A 1D array: For arbitrary waveforms, which must be paired with ``t`` for timing.

    :type f: float or numpy.ndarray
    :param t:
        Timing of the pulse(s) in seconds (s).
        Used when ``f`` is a 1D array to specify an arbitrary waveform.
    :type t: float or numpy.ndarray
    :param float tx_power:
        Transmitter power in decibels-milliwatts (dBm).
    :param int pulses:
        Total number of pulses.
    :param prp:
        Pulse repetition period (PRP) in seconds (s).
        Must satisfy ``prp >= pulse_length``.

        - If ``prp`` is ``None``, it defaults to ``pulse_length``.
        - Can also be a 1D array to specify different PRPs for each pulse.
          In this case, the array length must match ``pulses``.

    :type prp: float or numpy.ndarray
    :param numpy.ndarray f_offset:
        Frequency offset for each pulse in Hertz (Hz).
        Length must match ``pulses``. Default: ``None`` (no offset).
    :param numpy.ndarray pn_f:
        Frequencies associated with phase noise in Hertz (Hz).
        Must be paired with ``pn_power``. Default: ``None``.
    :param numpy.ndarray pn_power:
        Power spectral density of phase noise in dB/Hz.
        Must be paired with ``pn_f``. Default: ``None``.
    :param list[dict] channels:
        Properties of transmitter channels.
        Each channel is represented as a dictionary with the following keys:

        - **location** (*numpy.ndarray*):
          3D location of the channel relative to the radar [x, y, z] in meters.
        - **polarization** (*numpy.ndarray*):
          Antenna polarization vector [x, y, z].
          Default: ``[0, 0, 1]`` (vertical polarization).
          Examples:

            - Vertical polarization: ``[0, 0, 1]``
            - Horizontal polarization: ``[0, 1, 0]``
            - Right-handed circular polarization: ``[0, 1, 1j]``
            - Left-handed circular polarization: ``[0, 1, -1j]``

        - **delay** (*float*): Transmit delay (s). Default: ``0``.
        - **azimuth_angle** (*numpy.ndarray*): Azimuth angles in degrees (°).
          Default: ``[-90, 90]``.
        - **azimuth_pattern** (*numpy.ndarray*): Azimuth pattern in decibels (dB).
          Default: ``[0, 0]``.
        - **elevation_angle** (*numpy.ndarray*): Elevation angles in degrees (°).
          Default: ``[-90, 90]``.
        - **elevation_pattern** (*numpy.ndarray*): Elevation pattern in decibels (dB).
          Default: ``[0, 0]``.
        - **grid** (*float*):
          The grid size in degrees (°) used to initially check the occupancy of a scene.
          Default: ``1``.
        - **pulse_amp** (*numpy.ndarray*):
          Relative amplitude sequence for pulse amplitude modulation.
          Length must match ``pulses``. Default: ``1``.
        - **pulse_phs** (*numpy.ndarray*):
          Phase code sequence for pulse phase modulation in degrees (°).
          Length must match ``pulses``. Default: ``0``.
        - **mod_t** (*numpy.ndarray*): Timestamps for waveform modulation in seconds (s).
          Default: ``None``.
        - **phs** (*numpy.ndarray*): Phase modulation scheme in degrees (°).
          Default: ``None``.
        - **amp** (*numpy.ndarray*): Relative amplitude scheme for waveform modulation.
          Default: ``None``.

    :ivar dict rf_prop:
        RF properties of the transmitter:

        - **tx_power** (*float*): Transmitter power in dBm.
        - **pn_f** (*numpy.ndarray*): Frequencies associated with phase noise (Hz).
        - **pn_power** (*numpy.ndarray*): Power of phase noise (dB/Hz).

    :ivar dict waveform_prop:
        Waveform properties:

        - **f** (*float or numpy.ndarray*): Waveform frequency (Hz).
        - **t** (*float or numpy.ndarray*): Timing of each pulse (s).
        - **bandwidth** (*float*): Transmitting bandwidth (Hz).
        - **pulse_length** (*float*): Duration of each pulse (s).
        - **pulses** (*int*): Total number of pulses.
        - **f_offset** (*numpy.ndarray*): Frequency offset for each pulse (Hz).
        - **prp** (*float or numpy.ndarray*): Pulse repetition period (s).
        - **pulse_start_time** (*numpy.ndarray*): Start times of each pulse (s).

    :ivar dict txchannel_prop:
        Properties of the transmitter channels:

        - **size** (*int*): Number of transmitter channels.
        - **delay** (*numpy.ndarray*): Transmitter start delay (s).
        - **grid** (*float*): Ray tracing grid size (°).
        - **locations** (*numpy.ndarray*):
          3D locations of the transmitter channels [x, y, z] in meters.
        - **polarization** (*numpy.ndarray*): Polarization vectors of the transmitter channels.
        - **waveform_mod** (*dict*): Waveform modulation parameters.
        - **pulse_mod** (*dict*): Pulse modulation parameters.
        - **az_angles** (*numpy.ndarray*): Azimuth angles (°).
        - **az_patterns** (*numpy.ndarray*): Azimuth patterns (dB).
        - **el_angles** (*numpy.ndarray*): Elevation angles (°).
        - **el_patterns** (*numpy.ndarray*): Elevation patterns (dB).
        - **antenna_gains** (*numpy.ndarray*): Transmitter antenna gains (dB).

    **Waveform Schematic**:

    Illustration of the waveform, pulse repetition period, and modulation:

    ::

        █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █
        █                        prp                                            █
        █                   +-----------+                                       █
        █       +---f[1]--------->  /            /            /                 █
        █                          /            /            /                  █
        █                         /            /            /                   █
        █                        /            /            /                    █
        █                       /            /            /     ...             █
        █                      /            /            /                      █
        █                     /            /            /                       █
        █                    /            /            /                        █
        █       +---f[0]--->/            /            /                         █
        █                   +-------+                                           █
        █                  t[0]    t[1]                                         █
        █                                                                       █
        █     Pulse         +--------------------------------------+            █
        █     modulation    |pulse_amp[0]|pulse_amp[1]|pulse_amp[2]|  ...       █
        █                   |pulse_phs[0]|pulse_phs[1]|pulse_phs[2]|  ...       █
        █                   +--------------------------------------+            █
        █                                                                       █
        █     Waveform      +--------------------------------------+            █
        █     modulation    |           amp / phs / mod_t          |  ...       █
        █                   +--------------------------------------+            █
        █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █

    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        f: Union[float, List, NDArray],
        t: Union[float, List, NDArray],
        tx_power: float = 0,
        pulses: int = 1,
        prp: Optional[Union[float, NDArray]] = None,
        f_offset: Optional[Union[float, NDArray]] = None,
        pn_f: Optional[NDArray] = None,
        pn_power: Optional[NDArray] = None,
        channels: Optional[List[Dict]] = None,
    ):
        self.rf_prop = {}
        self.waveform_prop = {}
        self.txchannel_prop = {}

        self.rf_prop["tx_power"] = tx_power
        self.rf_prop["pn_f"] = pn_f
        self.rf_prop["pn_power"] = pn_power
        self.validate_rf_prop(self.rf_prop)

        # get `f(t)`
        # the lenght of `f` should be the same as `t`
        if isinstance(f, (list, tuple, np.ndarray)):
            f = np.array(f)
        else:
            f = np.array([f, f])

        if isinstance(t, (list, tuple, np.ndarray)):
            t = np.array(t) - t[0]
        else:
            t = np.array([0, t])

        self.waveform_prop["f"] = f
        self.waveform_prop["t"] = t
        self.waveform_prop["bandwidth"] = np.max(f) - np.min(f)
        self.waveform_prop["pulse_length"] = t[-1]
        self.waveform_prop["pulses"] = pulses

        # frequency offset for each pulse
        # the length of `f_offset` should be the same as `pulses`
        if f_offset is None:
            f_offset = np.zeros(pulses)
        else:
            if isinstance(f_offset, (list, tuple, np.ndarray)):
                f_offset = np.array(f_offset)
            else:
                f_offset = f_offset + np.zeros(pulses)
        self.waveform_prop["f_offset"] = f_offset

        # Extend `prp` to a numpy.1darray.
        # Length equels to `pulses`
        if prp is None:
            prp = self.waveform_prop["pulse_length"] + np.zeros(pulses)
        else:
            if isinstance(prp, (list, tuple, np.ndarray)):
                prp = np.array(prp)
            else:
                prp = prp + np.zeros(pulses)
        self.waveform_prop["prp"] = prp

        # start time of each pulse, without considering the delay
        self.waveform_prop["pulse_start_time"] = np.cumsum(prp) - prp[0]

        self.validate_waveform_prop(self.waveform_prop)

        if channels is None:
            channels = [{"location": (0, 0, 0)}]

        self.txchannel_prop = self.process_txchannel_prop(channels)

    def validate_rf_prop(self, rf_prop: Dict) -> None:
        """
        Validate RF properties

        :param dict rf_prop: RF properties

        :raises ValueError: Lengths of `pn_f` and `pn_power` should be the same
        :raises ValueError: Lengths of `pn_f` and `pn_power` should be the same
        :raises ValueError: Lengths of `pn_f` and `pn_power` should be the same
        """
        if rf_prop["pn_f"] is not None and rf_prop["pn_power"] is None:
            raise ValueError("Lengths of `pn_f` and `pn_power` should be the same")
        if rf_prop["pn_f"] is None and rf_prop["pn_power"] is not None:
            raise ValueError("Lengths of `pn_f` and `pn_power` should be the same")
        if rf_prop["pn_f"] is not None and rf_prop["pn_power"] is not None:
            if len(rf_prop["pn_f"]) != len(rf_prop["pn_power"]):
                raise ValueError("Lengths of `pn_f` and `pn_power` should be the same")

    def validate_waveform_prop(self, waveform_prop: Dict) -> None:
        """
        Validate waveform properties

        :param waveform_prop (dict): Wavefrom properties

        :raises ValueError: Lengths of `f` and `t` should be the same
        :raises ValueError: Lengths of `f_offset` and `pulses` should be the same
        :raises ValueError: Length of `prp` should equal to the length of `pulses`
        :raises ValueError: `prp` should be larger than `pulse_length`
        """
        if len(waveform_prop["f"]) != len(waveform_prop["t"]):
            raise ValueError("Lengths of `f` and `t` should be the same")

        if len(waveform_prop["f_offset"]) != waveform_prop["pulses"]:
            raise ValueError("Lengths of `f_offset` and `pulses` should be the same")

        if len(waveform_prop["prp"]) != waveform_prop["pulses"]:
            raise ValueError("Length of `prp` should equal to the length of `pulses`")

        if np.min(waveform_prop["prp"]) < waveform_prop["pulse_length"]:
            raise ValueError("`prp` should be larger than `pulse_length`")

    def process_waveform_modulation(
        self, mod_t: Optional[NDArray], amp: Optional[NDArray], phs: Optional[NDArray]
    ) -> Dict:
        """
        Process waveform modulation parameters

        :param numpy.1darray mod_t: Time stamps for waveform modulation (s). ``default None``
        :param numpy.1darray amp:
            Relative amplitude scheme for waveform modulation. ``default None``
        :param numpy.1darray phs: Phase scheme for waveform modulation (deg). ``default None``

        :raises ValueError: Lengths of `amp` and `phs` should be the same
        :raises ValueError: Lengths of `mod_t`, `amp`, and `phs` should be the same

        :return:
            Waveform modulation
        :rtype: dict
        """

        if phs is not None and amp is None:
            amp = np.ones_like(phs)
        elif phs is None and amp is not None:
            phs = np.zeros_like(amp)

        if mod_t is None or amp is None or phs is None:
            return {"enabled": False, "var": None, "t": None}

        if isinstance(amp, (list, tuple, np.ndarray)):
            amp = np.array(amp)
        else:
            amp = np.array([amp, amp])

        if isinstance(phs, (list, tuple, np.ndarray)):
            phs = np.array(phs)
        else:
            phs = np.array([phs, phs])

        if isinstance(mod_t, (list, tuple, np.ndarray)):
            mod_t = np.array(mod_t)
        else:
            mod_t = np.array([0, mod_t])

        if len(amp) != len(phs):
            raise ValueError("Lengths of `amp` and `phs` should be the same")

        mod_var = amp * np.exp(1j * phs / 180 * np.pi)

        if len(mod_t) != len(mod_var):
            raise ValueError("Lengths of `mod_t`, `amp`, and `phs` should be the same")

        return {"enabled": True, "var": mod_var, "t": mod_t}

    def process_pulse_modulation(
        self, pulse_amp: NDArray, pulse_phs: NDArray
    ) -> NDArray:
        """
        Process pulse modulation parameters

        :param numpy.1darray pulse_amp:
            Relative amplitude sequence for pulse's amplitude modulation.
            The array length should be the same as `pulses`. ``default 1``
        :param numpy.1darray pulse_phs:
            Phase code sequence for pulse's phase modulation (deg).
            The array length should be the same as `pulses`. ``default 0``

        :raises ValueError: Lengths of `pulse_amp` and `pulses` should be the same
        :raises ValueError: Length of `pulse_phs` and `pulses` should be the same

        :return:
            Pulse modulation array
        :rtype: numpy.1darray
        """
        if len(pulse_amp) != self.waveform_prop["pulses"]:
            raise ValueError("Lengths of `pulse_amp` and `pulses` should be the same")
        if len(pulse_phs) != self.waveform_prop["pulses"]:
            raise ValueError("Length of `pulse_phs` and `pulses` should be the same")

        return np.array(pulse_amp) * np.exp(1j * (np.array(pulse_phs) / 180 * np.pi))

    def process_txchannel_prop(self, channels: List[Dict]) -> Dict:
        """
        Process transmitter channel parameters

        :param dict channels: Dictionary of transmitter channels

        :raises ValueError: Lengths of `azimuth_angle` and `azimuth_pattern`
            should be the same
        :raises ValueError: Lengths of `elevation_angle` and `elevation_pattern`
            should be the same

        :return:
            Transmitter channel properties
        :rtype: dict
        """
        # number of transmitter channels
        txch_prop = {}

        txch_prop["size"] = len(channels)

        # firing delay for each channel
        txch_prop["delay"] = np.zeros(txch_prop["size"])
        txch_prop["grid"] = np.zeros(txch_prop["size"])
        txch_prop["locations"] = np.zeros((txch_prop["size"], 3))
        txch_prop["polarization"] = np.zeros((txch_prop["size"], 3))

        # waveform modulation parameters
        txch_prop["waveform_mod"] = []

        # pulse modulation parameters
        txch_prop["pulse_mod"] = np.ones(
            (txch_prop["size"], self.waveform_prop["pulses"]), dtype=complex
        )

        # azimuth patterns
        txch_prop["az_patterns"] = []
        txch_prop["az_angles"] = []

        # elevation patterns
        txch_prop["el_patterns"] = []
        txch_prop["el_angles"] = []

        # antenna peak gain
        # antenna gain is calculated based on azimuth pattern
        txch_prop["antenna_gains"] = np.zeros((txch_prop["size"]))

        for tx_idx, tx_element in enumerate(channels):
            txch_prop["delay"][tx_idx] = tx_element.get("delay", 0)
            txch_prop["grid"][tx_idx] = tx_element.get("grid", 1)

            txch_prop["locations"][tx_idx, :] = np.array(tx_element.get("location"))
            txch_prop["polarization"][tx_idx, :] = np.array(
                tx_element.get("polarization", [0, 0, 1])
            )

            txch_prop["waveform_mod"].append(
                self.process_waveform_modulation(
                    tx_element.get("mod_t", None),
                    tx_element.get("amp", None),
                    tx_element.get("phs", None),
                )
            )

            txch_prop["pulse_mod"][tx_idx, :] = self.process_pulse_modulation(
                tx_element.get("pulse_amp", np.ones((self.waveform_prop["pulses"]))),
                tx_element.get("pulse_phs", np.zeros((self.waveform_prop["pulses"]))),
            )

            # azimuth pattern
            az_angle = np.array(tx_element.get("azimuth_angle", [-90, 90]))
            az_pattern = np.array(tx_element.get("azimuth_pattern", [0, 0]))
            if len(az_angle) != len(az_pattern):
                raise ValueError(
                    "Lengths of `azimuth_angle` and `azimuth_pattern` \
                        should be the same"
                )

            txch_prop["antenna_gains"][tx_idx] = np.max(az_pattern)
            az_pattern = az_pattern - txch_prop["antenna_gains"][tx_idx]

            txch_prop["az_angles"].append(az_angle)
            txch_prop["az_patterns"].append(az_pattern)

            # elevation pattern
            el_angle = np.array(tx_element.get("elevation_angle", [-90, 90]))
            el_pattern = np.array(tx_element.get("elevation_pattern", [0, 0]))
            if len(el_angle) != len(el_pattern):
                raise ValueError(
                    "Lengths of `elevation_angle` and `elevation_pattern` \
                        should be the same"
                )
            el_pattern = el_pattern - np.max(el_pattern)

            txch_prop["el_angles"].append(el_angle)
            txch_prop["el_patterns"].append(el_pattern)

        return txch_prop
