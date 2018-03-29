"""
Base class for the over-sampling method.
"""
# Authors: Guillaume Lemaitre <g.lemaitre58@gmail.com>
#          Christos Aridas
# License: MIT

from ..base import BaseSampler


class BaseOverSampler(BaseSampler):
    """Base class for over-sampling algorithms.

    Warning: This class should not be used directly. Use the derive classes
    instead.
    """

    _sampling_type = 'over-sampling'

    _sampling_target_docstring = \
        """sampling_target : float, str, dict or callable, (default='auto')
        Sampling information to resample the data set.

        - When ``float``, it correspond to the ratio :math:`\\alpha_{os}`
          defined by :math:`N_{rm} = \\alpha_{os} \\times N_{m}` where
          :math:`N_{rm}` and :math:`N_{M}` are the number of samples in the
          minority class after resampling and the number of samples in the
          majority class, respectively.

        .. warning::
           ``float`` is only available for **binary** classification. An error
           is raised for multi-class classification.

        - When ``str``, specify the class targeted by the resampling. The
          number of samples in the different classes will be equalized.
          Possible choices are:

            ``'minority'``: resample only the minority class;

            ``'majority'``: resample only the majority class;

            ``'not minority'``: resample all classes but the minority class;

            ``'not majority'``: resample all classes but the majority class;

            ``'all'``: resample all classes;

            ``'auto'``: equivalent to ``'not majority'``.

        - When ``dict``, the keys correspond to the targeted classes. The
          values correspond to the desired number of samples for each targeted
          class.

        - When callable, function taking ``y`` and returns a ``dict``. The keys
          correspond to the targeted classes. The values correspond to the
          desired number of samples for each class.
        """.strip()
