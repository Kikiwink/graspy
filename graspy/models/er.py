from .sbm import SBMEstimator, DCSBMEstimator
from ..utils import import_graph
import numpy as np


class EREstimator(SBMEstimator):
    """
    Erdos-Reyni Model 

    The Erdos-Reyni (ER) model is a simple random graph model in which the probability
    of any potential edge in the graph existing is the same for any two nodes :math:`i`
    and :math:`j`. 

    :math:`P_{ij} = p` for all i, j

    Parameters
    ----------
    directed : boolean, optional (default=True)
        Whether to treat the input graph as directed. Even if a directed graph is inupt, 
        this determines whether to force symmetry upon the block probability matrix fit
        for the SBM. It will also determine whether graphs sampled from the model are 
        directed. 
    loops : boolean, optional (default=False)
        Whether to allow entries on the diagonal of the adjacency matrix, i.e. loops in 
        the graph where a node connects to itself. 

    See also
    --------
    graspy.models.DCEREstimator
    graspy.models.SBMEstimator
    graspy.simulations.er_np

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93R%C3%A9nyi_model
    """

    def __init__(self, directed=True, loops=False):
        super().__init__(directed=directed, loops=loops)

    def fit(self, graph, y=None):
        graph = import_graph(graph)
        er = super().fit(graph, y=np.ones(graph.shape[0]))
        self.p_ = er.block_p_[0, 0]
        delattr(self, "block_p_")
        return self

    def _n_parameters(self):
        n_parameters = 1  # p
        return n_parameters


class DCEREstimator(DCSBMEstimator):
    r"""
    Degree-corrected Erdos-Reyni Model 

    The Degree-corrected Erdos-Reyni (DCER) model is an extension of the ER model in 
    which each node has an additional "promiscuity" parameter :math:`\theta_i` that 
    determines its expected degree in the graph. 

    :math:`P_{ij} = \theta_i \theta_j p`

    Parameters
    ----------
    directed : boolean, optional (default=True)
        Whether to treat the input graph as directed. Even if a directed graph is inupt, 
        this determines whether to force symmetry upon the block probability matrix fit
        for the SBM. It will also determine whether graphs sampled from the model are 
        directed. 
    loops : boolean, optional (default=False)
        Whether to allow entries on the diagonal of the adjacency matrix, i.e. loops in 
        the graph where a node connects to itself. 
    degree_directed : boolean 
        Whether to allow seperate degree correction parameters for the in and out degree
        of each node. Ignored if `directed` is False.
    
    Notes
    -----
    The DCER model is rarely (if ever) mentioned in literature, though it is simply
    a special case of the DCSBM where there is only one community.

    See also
    --------
    graspy.models.DCSBMEstimator
    graspy.models.EREstimator
    graspy.simulations.er_np

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93R%C3%A9nyi_model
    .. [2]  Karrer, B., & Newman, M. E. (2011). Stochastic blockmodels and community
            structure in networks. Physical review E, 83(1), 016107.

    """

    def __init__(self, directed=True, loops=False, degree_directed=False):
        super().__init__(
            directed=directed, loops=loops, degree_directed=degree_directed
        )

    def fit(self, graph, y=None):
        dcer = super().fit(graph, y=np.ones(graph.shape[0]))
        self.p_ = dcer.block_p_[0, 0]
        delattr(self, "block_p_")
        return self

    def _n_parameters(self):
        n_parameters = 1  # p
        n_parameters += self.degree_corrections_.size
        return n_parameters
