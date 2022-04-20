# -*- coding: utf-8 -*-
"""Time Convolutional Neural Network (CNN) for classification."""

__author__ = ["James-Large", "TonyBagnall"]
__all__ = ["CNNClassifier"]
from sklearn.utils import check_random_state

from sktime.classification.deep_learning.base import BaseDeepClassifier
from sktime.networks.cnn import CNNNetwork
from sktime.utils.validation._dependencies import _check_soft_dependencies

_check_soft_dependencies("tensorflow", severity="error")


class CNNClassifier(BaseDeepClassifier, CNNNetwork):
    """Time Convolutional Neural Network (CNN), as described in [1].

    Parameters
    ----------
    should inherited fields be listed here?
    n_epochs       : int, default = 2000
        the number of epochs to train the model
    batch_size      : int, default = 16
        the number of samples per gradient update.
    kernel_size     : int, default = 7
        the length of the 1D convolution window
    avg_pool_size   : int, default = 3
        size of the average pooling windows
    n_conv_layers   : int, default = 2
        the number of convolutional plus average pooling layers
    filter_sizes    : array of shape (n_conv_layers) default = [6, 12]
    random_state    : int or None, default=None
        Seed for random number generation.
    verbose         : boolean, default = False
        whether to output extra information
    loss            : string, default="mean_squared_error"
        fit parameter for the keras model
    optimizer       : keras.optimizer, default=keras.optimizers.Adam(),
    metrics         : list of strings, default=["accuracy"],

    Notes
    -----
    ..[1] Zhao et. al, Convolutional neural networks for
    time series classification, Journal of
    Systems Engineering and Electronics, 28(1):2017.

    Adapted from the implementation from Fawaz et. al
    https://github.com/hfawaz/dl-4-tsc/blob/master/classifiers/cnn.py
    """

    def __init__(
        self,
        n_epochs=2000,
        batch_size=16,
        kernel_size=7,
        avg_pool_size=3,
        n_conv_layers=2,
        callbacks=None,
        verbose=False,
    ):
        super(CNNClassifier, self).__init__()
        self.n_conv_layers = n_conv_layers
        self.avg_pool_size = avg_pool_size
        self.kernel_size = kernel_size
        self.callbacks = callbacks
        self.n_epochs = n_epochs
        self.batch_size = batch_size
        self.verbose = verbose

    def build_model(self, input_shape, n_classes, **kwargs):
        """Construct a compiled, un-trained, keras model that is ready for training.

        Parameters
        ----------
        input_shape : tuple
            The shape of the data fed into the input layer, should be (m,d)
        n_classes: int
            The number of classes, which becomes the size of the output layer

        Returns
        -------
        output : a compiled Keras Model
        """
        from tensorflow import keras

        input_layer, output_layer = self.build_network(input_shape, **kwargs)

        output_layer = keras.layers.Dense(units=n_classes, activation="sigmoid")(
            output_layer
        )

        model = keras.models.Model(inputs=input_layer, outputs=output_layer)
        model.compile(
            loss="mean_squared_error",
            optimizer=keras.optimizers.Adam(),
            metrics=["accuracy"],
        )
        return model

    def _fit(self, X, y):
        """Fit the classifier on the training set (X, y).

        Parameters
        ----------
        X : np.ndarray of shape = (n_instances, n_dimensions, series_length)
            The training input samples.
        y : np.ndarray of shape = [n_instances]
            The training data class labels.
        input_checks : boolean
            whether to check the X and y parameters
        validation_X : np.ndarray of shape = (n_instances, n_dimensions, series_length)
            The validation samples.
            Unless strictly defined by the user via callbacks (such as
            EarlyStopping), the presence or state of the validation
            data does not alter training in any way. Predictions at each epoch
            are stored in the model's fit history.
        validation_y : np.ndarray of shape = [n_instances]
            The validation class labels.

        Returns
        -------
        self : object
        """
        if self.callbacks is None:
            self._callbacks = []
        y_onehot = self.convert_y_to_keras(y)
        # Transpose to conform to Keras input style.
        X = X.transpose(0, 2, 1)

        check_random_state(self.random_state)
        self.input_shape = X.shape[1:]
        self.model_ = self.build_model(self.input_shape, self.n_classes_)
        if self.verbose:
            self.model.summary()
        self.history = self.model_.fit(
            X,
            y_onehot,
            batch_size=self.batch_size,
            epochs=self.n_epochs,
            verbose=self.verbose,
            callbacks=self._callbacks,
        )
        return self
