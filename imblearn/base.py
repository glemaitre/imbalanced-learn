﻿"""Base class for sampling"""

# Authors: Guillaume Lemaitre <g.lemaitre58@gmail.com>
#          Christos Aridas
# License: MIT

from abc import ABCMeta, abstractmethod

import numpy as np

from sklearn.base import BaseEstimator
from sklearn.preprocessing import label_binarize
from sklearn.utils import check_X_y
from sklearn.utils.multiclass import check_classification_targets

from .utils import check_sampling_strategy, check_target_type


class SamplerMixin(BaseEstimator, metaclass=ABCMeta):
    """Mixin class for samplers with abstract method.

    Warning: This class should not be used directly. Use the derive classes
    instead.
    """

    _estimator_type = "sampler"

    def fit(self, X, y):
        """Check inputs and statistics of the sampler.

        You should use ``fit_resample`` in all cases.

        Parameters
        ----------
        X : {array-like, dataframe, sparse matrix} of shape \
                (n_samples, n_features)
            Data array.

        y : array-like of shape (n_samples,)
            Target array.

        Returns
        -------
        self : object
            Return the instance itself.
        """
        X, y, _ = self._check_X_y(X, y)
        self.sampling_strategy_ = check_sampling_strategy(
            self.sampling_strategy, y, self._sampling_type
        )
        return self

    def fit_resample(self, X, y):
        """Resample the dataset.

        Parameters
        ----------
        X : {array-like, dataframe, sparse matrix} of shape \
                (n_samples, n_features)
            Matrix containing the data which have to be sampled.

        y : array-like of shape (n_samples,)
            Corresponding label for each sample in X.

        Returns
        -------
        X_resampled : {array-like, dataframe, sparse matrix} of shape \
                (n_samples_new, n_features)
            The array containing the resampled data.

        y_resampled : array-like of shape (n_samples_new,)
            The corresponding label of `X_resampled`.
        """
        check_classification_targets(y)
        X, y, binarize_y = self._check_X_y(X, y)

        self.sampling_strategy_ = check_sampling_strategy(
            self.sampling_strategy, y, self._sampling_type
        )

        output = self._fit_resample(X, y)

        if self._X_columns is not None or self._y_name is not None:
            import pandas as pd

        if self._X_columns is not None:
            X_ = pd.DataFrame(output[0], columns=self._X_columns)
            X_ = X_.astype(self._X_dtypes)
        else:
            X_ = output[0]

        y_ = (label_binarize(output[1], np.unique(y))
              if binarize_y else output[1])

        if self._y_name is not None:
            y_ = pd.Series(y_, dtype=self._y_dtype, name=self._y_name)

        if binarize_y:
            if len(output) == 2:
                return X_, y_
            return X_, y_, output[2]
        if len(output) == 2:
            return X_, y_
        return X_, y_, output[2]

    #  define an alias for back-compatibility
    fit_sample = fit_resample

    @abstractmethod
    def _fit_resample(self, X, y):
        """Base method defined in each sampler to defined the sampling
        strategy.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            Matrix containing the data which have to be sampled.

        y : array-like of shape (n_samples,)
            Corresponding label for each sample in X.

        Returns
        -------
        X_resampled : {ndarray, sparse matrix} of shape \
                (n_samples_new, n_features)
            The array containing the resampled data.

        y_resampled : ndarray of shape (n_samples_new,)
            The corresponding label of `X_resampled`.

        """
        pass


class BaseSampler(SamplerMixin):
    """Base class for sampling algorithms.

    Warning: This class should not be used directly. Use the derive classes
    instead.
    """

    def __init__(self, sampling_strategy="auto"):
        self.sampling_strategy = sampling_strategy

    def _check_X_y(self, X, y, accept_sparse=None):
        if hasattr(X, "loc"):
            # store information to build dataframe
            self._X_columns = X.columns
            self._X_dtypes = X.dtypes
        else:
            self._X_columns = None
            self._X_dtypes = None

        if hasattr(y, "loc"):
            # store information to build a series
            self._y_name = y.name
            self._y_dtype = y.dtype
        else:
            self._y_name = None
            self._y_dtype = None

        if accept_sparse is None:
            accept_sparse = ["csr", "csc"]
        y, binarize_y = check_target_type(y, indicate_one_vs_all=True)
        X, y = check_X_y(X, y, accept_sparse=accept_sparse)
        return X, y, binarize_y


def _identity(X, y):
    return X, y


class FunctionSampler(BaseSampler):
    """Construct a sampler from calling an arbitrary callable.

    Read more in the :ref:`User Guide <function_sampler>`.

    Parameters
    ----------
    func : callable, default=None
        The callable to use for the transformation. This will be passed the
        same arguments as transform, with args and kwargs forwarded. If func is
        None, then func will be the identity function.

    accept_sparse : bool, default=True
        Whether sparse input are supported. By default, sparse inputs are
        supported.

    kw_args : dict, default=None
        The keyword argument expected by ``func``.

    validate : bool, default=True
        Whether or not to bypass the validation of ``X`` and ``y``. Turning-off
        validation allows to use the ``FunctionSampler`` with any type of
        data.

    See Also
    --------

    sklearn.preprocessing.FunctionTransfomer : Stateless transformer.

    Notes
    -----
    See
    :ref:`sphx_glr_auto_examples_plot_outlier_rejections.py`

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.datasets import make_classification
    >>> from imblearn import FunctionSampler
    >>> X, y = make_classification(n_classes=2, class_sep=2,
    ... weights=[0.1, 0.9], n_informative=3, n_redundant=1, flip_y=0,
    ... n_features=20, n_clusters_per_class=1, n_samples=1000, random_state=10)

    We can create to select only the first ten samples for instance.

    >>> def func(X, y):
    ...   return X[:10], y[:10]
    >>> sampler = FunctionSampler(func=func)
    >>> X_res, y_res = sampler.fit_resample(X, y)
    >>> np.all(X_res == X[:10])
    True
    >>> np.all(y_res == y[:10])
    True

    We can also create a specific function which take some arguments.

    >>> from collections import Counter
    >>> from imblearn.under_sampling import RandomUnderSampler
    >>> def func(X, y, sampling_strategy, random_state):
    ...   return RandomUnderSampler(
    ...       sampling_strategy=sampling_strategy,
    ...       random_state=random_state).fit_resample(X, y)
    >>> sampler = FunctionSampler(func=func,
    ...                           kw_args={'sampling_strategy': 'auto',
    ...                                    'random_state': 0})
    >>> X_res, y_res = sampler.fit_resample(X, y)
    >>> print('Resampled dataset shape {}'.format(
    ...     sorted(Counter(y_res).items())))
    Resampled dataset shape [(0, 100), (1, 100)]
    """

    _sampling_type = "bypass"

    def __init__(self, func=None, accept_sparse=True, kw_args=None,
                 validate=True):
        super().__init__()
        self.func = func
        self.accept_sparse = accept_sparse
        self.kw_args = kw_args
        self.validate = validate

    def fit_resample(self, X, y):
        """Resample the dataset.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            Matrix containing the data which have to be sampled.

        y : array-like of shape (n_samples,)
            Corresponding label for each sample in X.

        Returns
        -------
        X_resampled : {array-like, sparse matrix} of shape \
                (n_samples_new, n_features)
            The array containing the resampled data.

        y_resampled : array-like of shape (n_samples_new,)
            The corresponding label of `X_resampled`.
        """
        # store the columns name to reconstruct a dataframe
        self._columns = X.columns if hasattr(X, "loc") else None
        if self.validate:
            check_classification_targets(y)
            X, y, binarize_y = self._check_X_y(
                X, y, accept_sparse=self.accept_sparse
            )

        self.sampling_strategy_ = check_sampling_strategy(
            self.sampling_strategy, y, self._sampling_type
        )

        output = self._fit_resample(X, y)

        if self.validate:
            if self._X_columns is not None or self._y_name is not None:
                import pandas as pd

            if self._X_columns is not None:
                X_ = pd.DataFrame(output[0], columns=self._X_columns)
                X_ = X_.astype(self._X_dtypes)
            else:
                X_ = output[0]

            y_ = (label_binarize(output[1], np.unique(y))
                  if binarize_y else output[1])

            if self._y_name is not None:
                y_ = pd.Series(y_, dtype=self._y_dtype, name=self._y_name)

            if binarize_y:
                if len(output) == 2:
                    return X_, y_
                return X_, y_, output[2]
        else:
            X_, y_ = output[0], output[1]
            if len(output) == 2:
                return X_, y_
            return X_, y_, output[2]

    def _fit_resample(self, X, y):
        func = _identity if self.func is None else self.func
        output = func(X, y, **(self.kw_args if self.kw_args else {}))
        return output
