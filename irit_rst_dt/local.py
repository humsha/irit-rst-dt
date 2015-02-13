# pylint: disable=W0105
# pylint: disable=star-args
"""
Paths and settings used for this experimental harness
In the future we may move this to a proper configuration file.
"""

# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

import itertools

from attelo.harness.config import (EvaluationConfig,
                                   LearnerConfig,
                                   Learner,
                                   Variant)


LOCAL_TMP = 'TMP'
"""Things we may want to hold on to (eg. for weeks), but could
live with throwing away as needed"""

SNAPSHOTS = 'SNAPSHOTS'
"""Results over time we are making a point of saving"""

TRAINING_CORPORA = ['corpus/RSTtrees-WSJ-double-1.0']
"""Corpora for use in building/training models and running our
incremental experiments. Later on we should consider using the
held-out test data for something, but let's make a point of
holding it out for now.

Note that by convention, corpora are identified by their basename.
Something like `corpus/RSTtrees-WSJ-main-1.0/TRAINING` would result
in a corpus named "TRAINING". This could be awkward if the basename
is used in more than one corpus, but we can revisit this scheme as
needed.
"""

PTB_DIR = 'ptb3'
"""
Where to read the Penn Treebank from (should be dir corresponding to
parsed/mrg/wsj)
"""

_BASIC_LEARNERS =\
    [Variant(key=x, name=x, flags=[]) for x in
     ["bayes", "maxent"]]
"""Attelo learner algorithms to try.

It's up to you to choose values for the key field that can distinguish
between different configurations of your learners.  For example,
you might have something like

::

    Variant(key="perceptron-very-frob",
            name="perceptron",
            flags=["--frobnication", "0.9"]),

    Variant(key="perceptron-not-so-frob",
            name="perceptron",
            flags=["--frobnication", "0.4"])

"""
_FANCY_LEARNERS =\
    []
#    [Variant(key='perc-struct', name='perc-struct', flags=[])]
"""Attelo learners that take decoders as arguments.
We assume that they cannot be used relation modelling
"""


_CORE_DECODERS =\
    [Variant(key=x, name=x, flags=[]) for x in
     ["last", "local", "locallyGreedy", "mst", "astar"]]
"""Attelo decoders to try in experiment

Don't forget that you can parameterise the decoders ::

    Variant(key="astar-3-best",
            name="astar",
            flags=["--nbest", "3"])
"""

_GLOBAL_DECODER_SETTINGS =\
    [Variant(key='ADxL_joint', name=None,
             flags=[]),
     Variant(key='ADxL_post', name=None,
             flags=['--post-label'])]
"""Variants on global settings that would generally apply
over all decoder combos.

    Variant(key="post-label",
            name=None,
            flags=["--post-label"])

The name field is ignored here.

Note that not all global settings may be applicable to
all decoders.  For example, some learners may only
supoort '--post-label' decoding.

You may need to write some fancy logic when building the
EVALUATIONS list below in order to exclude these
possibilities
"""


def combined_key(variants):
    """return a key from a list of objects that have a
    `key` field each"""
    return '-'.join(v.key for v in variants)


def expanded_learners():
    """
    Some things we're trying to capture here:

    * in the basic case, you are using the same learner for
      the attachment and relation task

    * but some learners can't straightforwardly be used for
      multi-class classification so you have to use a
      different relation learner for them

    * some (fancy) learners are parameterised by decoders

    Suppose we have decoders (local, mst, astar) and the learners
    (maxent, struct-perceptron), the idea is that we would want
    to be able to generate the models:

        maxent (no parameterisation with decoders)
        struct-perceptron-mst
        struct-perceptron-astar


    Return a list of simple learners, and a list of decoder
    parameterised learners (as a functions)
    """
    simple =\
        [LearnerConfig(attach=Learner(key=l.key,
                                      name=l.name,
                                      flags=l.flags,
                                      decoder=None),
                       relate=None)
         for l in _BASIC_LEARNERS]

    # pylint: disable=cell-var-from-loop
    fancy = [lambda d:
             LearnerConfig(attach=Learner(key=learner.key,
                                          name=learner.name,
                                          flags=learner.flags,
                                          decoder=d),
                           relate=Learner(key="maxent",
                                          name="maxent",
                                          flags=[],
                                          decoder=None))
             for learner in _FANCY_LEARNERS]
    # pylint: enable=cell-var-from-loop
    return (simple, fancy)


def learner_decoder_pairs(decoders):
    """
    See :py:func:`learners_for_learning`

    Some other considerations:

    * in addition to decoders, there are variants on global
      decoder settings that we want to expand out; however,
      we do not want to expand this for purposes of model
      learning

    * if a learner is parameterised by a decoder, it should
      only be tested by the decoder it is parameterised
      against (along with variants on its global settings)

        - struct-perceptron-mst with the mst decoder
        - struct-perceptron-astar with the astar decoder

    * ideally (not mission-critical) we want to report all the
      struct-perceptron-* learners as struct-percepntron; but
      it's easy to accidentally do the wrong thing, so let's not
      bother, eh?

    This would be so much easier with static typing
    """
    simple, fancy = expanded_learners()
    simple_pairs = list(itertools.product(simple, decoders))
    fancy_pairs = []
    for learner in fancy:
        fancy_pairs.extend((learner(d), d) for d in decoders)
    return simple_pairs + fancy_pairs


def learners_for_learning(decoders):
    """
    Return a list of learner configurations that we would want
    to learn models for
    """
    simple, fancy = expanded_learners()
    res = simple
    for learner in fancy:
        res.extend([learner(d) for d in decoders])
    return res


def mk_config((learner, decoder), global_settings):
    """given a decoder and some global decoder settings,
    return an 'augmented' decoder reflecting these
    settings
    """
    decoder_key = combined_key([global_settings, decoder])
    decoder2 = Variant(key=decoder_key,
                       name=decoder.name,
                       flags=decoder.flags + global_settings.flags)
    return EvaluationConfig(key=combined_key([learner, decoder2]),
                            learner=learner,
                            decoder=decoder2)


LEARNERS = learners_for_learning(_CORE_DECODERS)
"""Learners that we would want to build models for"""

EVALUATIONS = [mk_config(*x) for x in
               itertools.product(learner_decoder_pairs(_CORE_DECODERS),
                                 _GLOBAL_DECODER_SETTINGS)]
"""Learners and decoders that are associated with each other.
The idea her is that if multiple decoders have a learner in
common, we will avoid rebuilding the model associated with
that learner.  For the most part we just want the cartesian
product, but some more sophisticated learners depend on the
their decoder, and cannot be shared
"""


ATTELO_CONFIG_FILE = "attelo.config"
"""Attelo feature configuration"""
