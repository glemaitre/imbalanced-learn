"""
The :mod:`imblearn.over_sampling` provides a set of method to
perform over-sampling.
"""

from ._adasyn import ADASYN
from ._random_over_sampler import RandomOverSampler
from ._smote import SMOTE
from ._smote import BorderlineSMOTE
from ._smote import SVMSMOTE

__all__ = ['ADASYN', 'RandomOverSampler',
           'SMOTE', 'BorderlineSMOTE', 'SVMSMOTE']
