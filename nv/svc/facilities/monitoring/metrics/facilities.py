# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""facilities monitoring metrics facilities."""
from time import perf_counter_ns
from typing import Dict, Optional

from nv.svc.core.facilities import base
from opentelemetry.metrics import Instrument, Meter, get_meter_provider
from opentelemetry.sdk.metrics import (Counter, Histogram, ObservableCounter,
                                       ObservableGauge,
                                       ObservableUpDownCounter, UpDownCounter)


class Timer:
    """Wrapper for generating _TimerHelper objects."""

    def __init__(self, histogram: Histogram):
        """
        Initialize the Timer.

        Parameters:
        - histogram (Histogram): The histogram to record the elapsed time.

        Returns:
        - Timer: An instance of the Timer class.
        """
        self._histogram = histogram

    def time(self, labels: Dict):
        """
        Create a new _TimerHelper instance for measuring time within a block of code.

        Parameters:
        - labels (Dict): Additional labels to associate with the recorded time.

        Returns:
        - _TimerHelper: A TimerHelper instance for measuring elapsed time.
        """
        return _TimerHelper(self._histogram, labels)


class _TimerHelper:
    """Helper timer context for recording the time a block of code takes to execute in milliseconds."""

    def __init__(self, histogram: Histogram, labels: Dict):
        """
        Initialize the _TimerHelper.

        Parameters:
        - histogram (Histogram): The histogram to record the elapsed time.
        - labels (Dict): Additional labels to associate with the recorded time.

        Returns:
        - _TimerHelper: An instance of the _TimerHelper class.
        """
        self._start = None
        self._histogram = histogram
        self._labels = labels

    def __enter__(self):
        """
        Enter the context and mark the beginning of the measurement.

        Returns:
        - None
        """
        self._start = perf_counter_ns()

    def __exit__(self, *exc_info):
        """
        Exit the context and record the elapsed time on the associated histogram.

        Parameters:
        - exc_info: Exception information.

        Returns:
        - None
        """
        # Determine the delta in milliseconds.
        delta = max(perf_counter_ns() - self._start, 0) / 1000000

        # Record on the histogram the elapsed time with the specified labels and a unit of milliseconds.
        modified_labels = self._labels.copy()
        modified_labels["unit"] = "milliseconds"
        self._histogram.record(delta, modified_labels)


class MetricsFacility(base.Facility):
    """Facility for managing metrics instruments."""

    def __init__(self, service: str, meter: Optional[Meter] = None):
        """
        Initialize the MetricsFacility.

        Parameters:
        - service (str): The identifier for the service associated with the metrics.
        - meter (Optional[Meter]): The meter to use for creating instruments. If not provided, a meter is obtained based on the service identifier.

        Returns:
        - MetricsFacility: An instance of the MetricsFacility class.
        """
        self._service = service

        self._metrics_instruments = {
            ObservableGauge: {},
            Histogram: {},
            ObservableCounter: {},
            Counter: {},
            ObservableUpDownCounter: {},
            UpDownCounter: {},
        }
        if meter:
            self._meter = meter
        else:
            self._meter = get_meter_provider().get_meter(self._service)

    def observable_gauge(self, name: str, unit: str, description: str, callbacks=None, **kwargs):
        """
        Create or retrieve an ObservableGauge instrument.

        Parameters:
        - name (str): The name of the gauge.
        - unit (str): The unit of measurement for the gauge.
        - description (str): A description of the gauge.
        - callbacks: Optional callbacks for the gauge.
        - kwargs: Additional keyword arguments.

        Returns:
        - Instrument: An instance of the ObservableGauge instrument.
        """
        return self._get_metrics_instrument(ObservableGauge, name, unit, description, callbacks=callbacks, **kwargs)

    def histogram(self, name: str, unit: str, description: str, **kwargs):
        """
        Create or retrieve a Histogram instrument.

        Parameters:
        - name (str): The name of the histogram.
        - unit (str): The unit of measurement for the histogram.
        - description (str): A description of the histogram.
        - kwargs: Additional keyword arguments.

        Returns:
        - Instrument: An instance of the Histogram instrument.
        """
        return self._get_metrics_instrument(Histogram, name, unit, description, **kwargs)

    def timer(self, name: str, description: str, **kwargs):
        """
        Create a Timer instance associated with a specific histogram.

        Parameters:
        - name (str): The name of the timer.
        - description (str): A description of the timer.
        - kwargs: Additional keyword arguments.

        Returns:
        - Timer: An instance of the Timer class.
        """
        unit = "milliseconds"
        histogram = self.histogram(name, unit, description, **kwargs)
        return Timer(histogram)

    def counter(self, name: str, unit: str, description: str, **kwargs):
        """
        Create or retrieve a Counter instrument.

        Parameters:
        - name (str): The name of the counter.
        - unit (str): The unit of measurement for the counter.
        - description (str): A description of the counter.
        - kwargs: Additional keyword arguments.

        Returns:
        - Instrument: An instance of the Counter instrument.
        """
        return self._get_metrics_instrument(Counter, name, unit, description, **kwargs)

    def observable_counter(self, name: str, unit: str, description: str, callbacks=None, **kwargs):
        """
        Create or retrieve an ObservableCounter instrument.

        Parameters:
        - name (str): The name of the ObservableCounter.
        - unit (str): The unit of measurement for the ObservableCounter.
        - description (str): A description of the ObservableCounter.
        - callbacks: Optional callbacks for the ObservableCounter.
        - kwargs: Additional keyword arguments.

        Returns:
        - Instrument: An instance of the ObservableCounter instrument.
        """
        return self._get_metrics_instrument(ObservableCounter, name, unit, description, callbacks=callbacks, **kwargs)

    def up_down_counter(self, name: str, unit: str, description: str, **kwargs):
        """
        Create or retrieve an UpDownCounter instrument.

        Parameters:
        - name (str): The name of the UpDownCounter.
        - unit (str): The unit of measurement for the UpDownCounter.
        - description (str): A description of the UpDownCounter.
        - kwargs: Additional keyword arguments.

        Returns:
        - Instrument: An instance of the UpDownCounter instrument.
        """
        return self._get_metrics_instrument(UpDownCounter, name, unit, description, **kwargs)

    def observable_up_down_counter(self, name: str, unit: str, description: str, callbacks=None, **kwargs):
        """
        Create or retrieve an ObservableUpDownCounter instrument.

        Parameters:
        - name (str): The name of the ObservableUpDownCounter.
        - unit (str): The unit of measurement for the ObservableUpDownCounter.
        - description (str): A description of the ObservableUpDownCounter.
        - callbacks: Optional callbacks for the ObservableUpDownCounter.
        - kwargs: Additional keyword arguments.

        Returns:
        - Instrument: An instance of the ObservableUpDownCounter instrument.
        """
        return self._get_metrics_instrument(ObservableUpDownCounter, name, unit, description, callbacks=callbacks, **kwargs)

    def _get_metrics_instrument(
        self,
        class_,
        name,
        unit,
        description,
        callbacks=None,
        namespace=None,
        subsystem=None,
        **kwargs
    ) -> Instrument:
        """
        Create or retrieve a metrics instrument based on the specified class.

        Parameters:
        - class_ (Instrument): The class of the instrument to create or retrieve.
        - name (str): The name of the instrument.
        - unit (str): The unit of measurement for the instrument.
        - description (str): A description of the instrument.
        - callbacks: Optional callbacks for instruments that support them.
        - namespace (str): An optional namespace for the instrument.
        - subsystem (str): An optional subsystem for the instrument.
        - kwargs: Additional keyword arguments.

        Returns:
        - Instrument: An instance of the specified instrument class.
        """
        namespace = f"{self._service}_{namespace}" if namespace else self._service
        key = hash((name, description, namespace, subsystem, unit, tuple(kwargs)))

        instrument = self._metrics_instruments[class_].get(key)

        if instrument:
            return instrument

        if class_ is Counter:
            instrument = self._meter.create_counter(name=name, unit=unit, description=description, **kwargs)
        elif class_ is UpDownCounter:
            instrument = self._meter.create_up_down_counter(name=name, unit=unit, description=description, **kwargs)
        elif class_ is ObservableCounter:
            callback_wrapper = [callbacks] if callable(callbacks) else callbacks
            instrument = self._meter.create_observable_counter(name=name, callbacks=callback_wrapper, unit=unit, description=description, **kwargs)
        elif class_ is ObservableUpDownCounter:
            callback_wrapper = [callbacks] if callable(callbacks) else callbacks
            instrument = self._meter.create_observable_up_down_counter(name=name, callbacks=callback_wrapper, unit=unit, description=description, **kwargs)
        elif class_ is ObservableGauge:
            callback_wrapper = [callbacks] if callable(callbacks) else callbacks
            instrument = self._meter.create_observable_gauge(name=name, callbacks=callback_wrapper, unit=unit, description=description, **kwargs)
        elif class_ is Histogram:
            instrument = self._meter.create_histogram(name=name, unit=unit, description=description, **kwargs)
        else:
            raise Exception("Unknown instrument type provided to MetricsFacility.")

        self._metrics_instruments[class_][key] = instrument
        return instrument
