import numpy as np

from .base import BaseGraphEstimator
from ..embed import AdjacencySpectralEmbed
from ..simulations import p_from_latent
from ..utils import import_graph, augment_diagonal, is_unweighted


class RDPGEstimator(BaseGraphEstimator):
    r"""
    Random Dot Product Graph

    Under the random dot product graph model, each node is assumed to have a
    "latent position" in some :math:`d`-dimensional Euclidian space. This vector 
    dictates that node's probability of connection to other nodes. For a given pair
    of nodes :math:`i` and :math:`j`, the probability of connection is the dot 
    product between their latent positions: 

    :math:`P_{ij} = \langle x_i, x_j \rangle`

    where :math:`x_i` and :math:`x_j` are the latent positions of nodes :math:`i` and
    :math:`j`, respectively.

    Parameters
    ----------
    loops : boolean, optional (default=False)
        Whether to allow entries on the diagonal of the adjacency matrix, i.e. loops in 
        the graph where a node connects to itself. 

    n_components : int, optional (default=None)
        The dimensionality of the latent space used to model the graph. If None, the
        method of Zhu and Godsie will be used to select an embedding dimension. 
    
    ase_kws : dict, optional (default={})
        Dictionary of keyword arguments passed down to 
        `graspy.embed.AdjacencySpectralEmbed`, which is used to fit the model.

    diag_aug_weight : int or float, optional (default=1)
        Weighting used for diagonal augmentation, which is a form of regularization for 
        fitting the RDPG model. 

    plus_c_weight : int or float, optional (default=1)
        Weighting used for a constant scalar added to the adjacency matrix before 
        embedding as a form of regularization.

    See also
    --------
    graspy.simulations.rdpg
    graspy.embed.AdjacencySpectralEmbed
    graspy.utils.augment_diagonal

    References
    ----------
    .. [1] Athreya, A., Fishkind, D. E., Tang, M., Priebe, C. E., Park, Y.,
           Vogelstein, J. T., ... & Sussman, D. L. (2018). Statistical inference
           on random dot product graphs: a survey. Journal of Machine Learning 
           Research, 18(226), 1-92.

    .. [2] Zhu, M. and Ghodsi, A. (2006).
           Automatic dimensionality selection from the scree plot via the use of
           profile likelihood. Computational Statistics & Data Analysis, 51(2), 
           pp.918-930.
    """

    def __init__(
        self,
        loops=False,
        n_components=None,
        ase_kws={},
        diag_aug_weight=1,
        plus_c_weight=1,
    ):
        super().__init__(loops=loops)

        if not isinstance(ase_kws, dict):
            raise TypeError("ase_kws must be a dict")
        if not isinstance(diag_aug_weight, (int, float)):
            raise TypeError("diag_aug_weight must be a scalar")
        if not isinstance(plus_c_weight, (int, float)):
            raise TypeError("plus_c_weight must be a scalar")
        if diag_aug_weight < 0:
            raise ValueError("diag_aug_weight must be at least 0")
        if plus_c_weight < 0:
            raise ValueError("plus_c_weight must be at least 0")

        self.n_components = n_components
        self.ase_kws = ase_kws
        self.diag_aug_weight = diag_aug_weight
        self.plus_c_weight = plus_c_weight

    def fit(self, graph, y=None):
        graph = import_graph(graph)
        if not is_unweighted(graph):
            raise NotImplementedError(
                "Graph model is currently only implemented for unweighted graphs."
            )
        graph = augment_diagonal(graph, weight=self.diag_aug_weight)
        graph += self.plus_c_weight / graph.size
        ase = AdjacencySpectralEmbed(n_components=self.n_components, **self.ase_kws)
        latent = ase.fit_transform(graph)
        self.latent_ = latent
        if type(self.latent_) == tuple:
            X = self.latent_[0]
            Y = self.latent_[1]
            self.directed = True
        else:
            X = self.latent_
            Y = self.latent_
            self.directed = False
        p_mat = X @ Y.T
        if not self.loops:
            p_mat -= np.diag(np.diag(p_mat))
        self.p_mat_ = p_mat
        return self

    def _n_parameters(self):
        if type(self.latent_) == tuple:
            return 2 * self.latent_[0].size
        else:
            return self.latent_.size
