"""
Paths and settings used for this experimental harness
In the future we may move this to a proper configuration file.
"""

# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

from __future__ import print_function
from collections import namedtuple
from os import path as fp
import itertools as itr
import six

import educe.stac.corpus
import numpy as np

from attelo.harness.config import (EvaluationConfig,
                                   LearnerConfig,
                                   Keyed)

from attelo.decoding.baseline import (LocalBaseline)
from attelo.decoding.local import (AsManyDecoder, BestIncomingDecoder)
from attelo.decoding.mst import (MstDecoder, MstRootStrategy)
from attelo.learning.perceptron import (Perceptron,
                                        PerceptronArgs,
                                        PassiveAggressive,
                                        StructuredPerceptron,
                                        StructuredPassiveAggressive)
from attelo.learning.local import (SklearnAttachClassifier,
                                   SklearnLabelClassifier)
from attelo.learning.oracle import (AttachOracle, LabelOracle)

from attelo.parser.intra import (HeadToHeadParser,
                                 IntraInterPair,
                                 SentOnlyParser,
                                 SoftParser)
from attelo.parser.full import (JointPipeline,
                                PostlabelPipeline)

from sklearn.linear_model import (LogisticRegression,
                                  Perceptron as SkPerceptron,
                                  PassiveAggressiveClassifier as
                                  SkPassiveAggressiveClassifier)
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# PATHS

CONFIG_FILE = fp.splitext(__file__)[0] + '.py'


LOCAL_TMP = 'TMP'
"""Things we may want to hold on to (eg. for weeks), but could
live with throwing away as needed"""

SNAPSHOTS = 'SNAPSHOTS'
"""Results over time we are making a point of saving"""

# TRAINING_CORPUS = 'tiny'
# TRAINING_CORPUS = 'corpus/RSTtrees-WSJ-main-1.0/TRAINING'
TRAINING_CORPUS = 'corpus/RSTtrees-WSJ-double-1.0'
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

TEST_CORPUS = None
# TEST_CORPUS = 'tiny'
"""Corpora for use in FINAL testing.

You should probably leave this set to None until you've tuned and
tweaked things to the point of being able to write up a paper.
Wouldn't want to overfit to the test corpus, now would we?

(If you leave this set to None, we will perform 10-fold cross
validation on the training data)
"""

TEST_EVALUATION_KEY = None
# TEST_EVALUATION_KEY = 'maxent-AD.L_jnt-mst'
"""Evaluation to use for testing.

Leave this to None until you think it's OK to look at the test data.
The key should be the evaluation key from one of your EVALUATIONS,
eg. 'maxent-C0.9-AD.L_jnt-mst'

(HINT: you can join them together from the report headers)
"""


PTB_DIR = 'ptb3'
"""
Where to read the Penn Treebank from (should be dir corresponding to
parsed/mrg/wsj)
"""

FEATURE_SET = 'dev'  # one of ['dev', 'eyk', 'li2014']
"""
Which feature set to use for feature extraction
"""

FIXED_FOLD_FILE = None
# FIXED_FOLD_FILE = 'folds-TRAINING.json'
"""
Set this to a file path if you *always* want to use it for your corpus
folds. This is for long standing evaluation experiments; we want to
ensure that we have the same folds across different evaluate experiments,
and even across different runs of gather.

NB. It's up to you to ensure that the folds file makes sense
"""


Settings = namedtuple('Settings',
                      ['key', 'intra', 'oracle', 'children'])
"""
Note that this is subclass of Keyed

The settings are used for config management only, for example,
if we want to filter in/out configurations that involve an
oracle.

Parameters
----------
intra: bool
    If this config uses intra/inter decoding

oracle: bool
    If parser should be considered oracle-based

children: container(Settings)
    Any nested settings (eg. if intra/inter, this would be the
    the settings of the intra and inter decoders)
"""

def combined_key(*variants):
    """return a key from a list of objects that have a
    `key` field each"""
    return '-'.join(v if isinstance(v, six.string_types) else v.key
                    for v in variants)

def decoder_last():
    "our instantiation of the mst decoder"
    return Keyed('last', LastBaseline())

def decoder_local():
    "our instantiation of the mst decoder"
    return Keyed('local', LocalBaseline(0.2, True))

def decoder_mst():
    "our instantiation of the mst decoder"
    return Keyed('mst', MstDecoder(MstRootStrategy.leftmost, True))


def attach_learner_oracle():
    "return a keyed instance of the oracle (virtual) learner"
    return Keyed('oracle', AttachOracle())


def label_learner_oracle():
    "return a keyed instance of the oracle (virtual) learner"
    return Keyed('oracle', LabelOracle())



def attach_learner_maxent():
    "return a keyed instance of maxent learner"
    return Keyed('maxent', SklearnAttachClassifier(LogisticRegression()))

def label_learner_maxent():
    "return a keyed instance of maxent learner"
    return Keyed('maxent', SklearnLabelClassifier(LogisticRegression()))



def attach_learner_dectree():
    "return a keyed instance of decision tree learner"
    return Keyed('dectree', SklearnAttachClassifier(DecisionTreeClassifier()))


def label_learner_dectree():
    "return a keyed instance of decision tree learner"
    return Keyed('dectree', SklearnLabelClassifier(DecisionTreeClassifier()))


def attach_learner_rndforest():
    "return a keyed instance of random forest learner"
    return Keyed('rndforest', SklearnAttachClassifier(RandomForestClassifier()))

def label_learner_rndforest():
    "return a keyed instance of decision tree learner"
    return Keyed('rndforest', SklearnLabelClassifier(RandomForestClassifier()))


def attach_learner_perc():
    "return a keyed instance of perceptron learner"
    return Keyed('perc', SklearnAttachClassifier(SkPerceptron(n_iter=20)))

def label_learner_perc():
    "return a keyed instance of perceptron learner"
    return Keyed('perc', SklearnLabelClassifier(SkPerceptron(n_iter=20)))


def attach_learner_pa():
    "return a keyed instance of passive aggressive learner"
    return Keyed('pa', SklearnAttachClassifier(SkPassiveAggressiveClassifier(n_iter=20)))

def label_learner_pa():
    "return a keyed instance of passive aggressive learner"
    return Keyed('pa', SklearnLabelClassifier(SkPassiveAggressiveClassifier(n_iter=20)))


LOCAL_PERC_ARGS = PerceptronArgs(iterations=20,
                                 averaging=True,
                                 use_prob=False,
                                 aggressiveness=np.inf)

def attach_learner_dp_perc():
    "return a keyed instance of perceptron learner"
    return Keyed('dp-perc', SklearnAttachClassifier(Perceptron(LOCAL_PERC_ARGS)))

def label_learner_dp_perc():
    "return a keyed instance of perceptron learner"
    return Keyed('dp-perc', SklearnLabelClassifier(Perceptron(LOCAL_PERC_ARGS)))


LOCAL_PA_ARGS = PerceptronArgs(iterations=20,
                               averaging=True,
                               use_prob=False,
                               aggressiveness=np.inf)

def attach_learner_dp_pa():
    "return a keyed instance of passive aggressive learner"
    return Keyed('dp-pa', SklearnAttachClassifier(PassiveAggressive(LOCAL_PA_ARGS)))

def label_learner_dp_pa():
    "return a keyed instance of passive aggressive learner"
    return Keyed('dp-pa', SklearnLabelClassifier(PassiveAggressive(LOCAL_PA_ARGS)))


STRUCT_PERC_ARGS = PerceptronArgs(iterations=50,
                                  averaging=True,
                                  use_prob=False,
                                  aggressiveness=np.inf)

STRUCT_PA_ARGS = PerceptronArgs(iterations=50,
                                averaging=True,
                                use_prob=False,
                                aggressiveness=np.inf)

ORACLE = LearnerConfig(attach=attach_learner_oracle(),
                       label=label_learner_oracle())

_LOCAL_LEARNERS = [
    ORACLE,
    LearnerConfig(attach=attach_learner_maxent(),
                  label=label_learner_maxent()),
#    LearnerConfig(attach=attach_learner_maxent(),
#                  label=label_learner_oracle()),
#    LearnerConfig(attach=attach_learner_rndforest(),
#                  label=label_learner_rndforest()),
#    LearnerConfig(attach=attach_learner_perc(),
#                  label=label_learner_maxent()),
#    LearnerConfig(attach=attach_learner_pa(),
#                  label=label_learner_maxent()),
#    LearnerConfig(attach=attach_learner_dp_perc(),
#                  label=label_learner_maxent()),
#    LearnerConfig(attach=attach_learner_dp_pa(),
#                  label=label_learner_maxent()),
]
"""Straightforward attelo learner algorithms to try

It's up to you to choose values for the key field that can distinguish
between different configurations of your learners.

"""

_STRUCTURED_LEARNERS = [
#    lambda d: LearnerConfig(attach=Keyed('dp-struct-perc',
#                                         StructuredPerceptron(d, STRUCT_PERC_ARGS)),
#                            label=learner_maxent()),
#    lambda d: LearnerConfig(attach=Keyed('dp-struct-pa',
#                                         StructuredPassiveAggressive(d, STRUCT_PA_ARGS)),
#                            label=learner_maxent()),
]

"""Attelo learners that take decoders as arguments.
We assume that they cannot be used relation modelling
"""

def _core_settings(key, klearner):
    "settings for basic pipelines"
    return Settings(key=key,
                    intra=False,
                    oracle='oracle' in klearner.key,
                    children=None)

def mk_joint(klearner, kdecoder):
    "return a joint decoding parser config"
    settings = _core_settings('AD.L-jnt', klearner)
    parser_key = combined_key(settings, kdecoder)
    key = combined_key(klearner, parser_key)
    parser = JointPipeline(learner_attach=klearner.attach.payload,
                           learner_label=klearner.label.payload,
                           decoder=kdecoder.payload)
    return EvaluationConfig(key=key,
                            settings=settings,
                            learner=klearner,
                            parser=Keyed(parser_key, parser))


def mk_post(klearner, kdecoder):
    "return a post label parser"
    settings = _core_settings('AD.L-pst', klearner)
    parser_key = combined_key(settings, kdecoder)
    key = combined_key(klearner, parser_key)
    parser = PostlabelPipeline(learner_attach=klearner.attach.payload,
                               learner_label=klearner.label.payload,
                               decoder=kdecoder.payload)
    return EvaluationConfig(key=key,
                            settings=settings,
                            learner=klearner,
                            parser=Keyed(parser_key, parser))


def _core_parsers(klearner):
    """Our basic parser configurations
    """
    return [
        # joint
        #mk_joint(klearner, decoder_last()),
        mk_joint(klearner, decoder_local()),
        #mk_joint(klearner, decoder_mst()),
        #mk_joint(klearner, tc_decoder(decoder_local())),
        mk_joint(klearner, tc_decoder(decoder_mst())),

        # postlabeling
        #mk_post(klearner, decoder_last()),
        mk_post(klearner, decoder_local()),
        #mk_post(klearner, decoder_mst()),
        #mk_post(klearner, tc_decoder(decoder_local())),
        mk_post(klearner, tc_decoder(decoder_mst())),
    ]


_INTRA_INTER_CONFIGS = [
    Keyed('iheads', HeadToHeadParser),
    Keyed('ionly', SentOnlyParser),
    Keyed('isoft', SoftParser),
]


# -------------------------------------------------------------------------------
# maybe less to edit below but still worth having a glance
# -------------------------------------------------------------------------------

HARNESS_NAME = 'irit-rst-dt'


def _is_junk(klearner, kdecoder):
    """
    Any configuration for which this function returns True
    will be silently discarded
    """
    # intrasential head to head mode only works with mst for now
    intra_flag = kdecoder.settings.intra
    if kdecoder.key != 'mst':
        if (intra_flag is not None and
                intra_flag.strategy == IntraStrategy.heads):
            return True

    # no need for intra/inter oracle mode if the learner already
    # is an oracle
    if klearner.key == 'oracle' and intra_flag is not None:
        if intra_flag.intra_oracle or intra_flag.inter_oracle:
            return True

    # skip any config which tries to use a non-prob learner with
    if not klearner.attach.payload.can_predict_proba:
        if kdecoder.settings.mode != DecodingMode.post_label:
            return True

    return False


def _mk_intra(mk_parser, settings):
    """
    Return an intra/inter parser that would be wrapped
    around a core parser
    """
    strategy = settings.strategy
    def _inner(lcfg):
        "the actual parser factory"
        oracle_cfg = LearnerConfig(attach=attach_learner_oracle(),
                                   label=label_learner_oracle())
        intra_cfg = oracle_cfg if settings.intra_oracle else lcfg
        inter_cfg = oracle_cfg if settings.inter_oracle else lcfg
        parsers = IntraInterPair(intra=mk_parser(intra_cfg),
                                 inter=mk_parser(inter_cfg))
        if strategy == IntraStrategy.only:
            return SentOnlyParser(parsers)
        elif strategy == IntraStrategy.heads:
            return HeadToHeadParser(parsers)
        elif strategy == IntraStrategy.soft:
            return SoftParser(parsers)
        else:
            raise ValueError("Unknown strategy: " + str(strategy))
    return _inner


def _mk_parser_config(kdecoder, settings):
    """construct a decoder from the settings

    :type k_decoder: Keyed(Settings -> Decoder)

    :rtype: ParserConfig
    """
    decoder_key = combined_key([settings, kdecoder])
    decoder = kdecoder.payload(settings)
    if settings.mode == DecodingMode.joint:
        mk_parser = lambda t: JointPipeline(learner_attach=t.attach.payload,
                                            learner_label=t.label.payload,
                                            decoder=decoder)
    elif settings.mode == DecodingMode.post_label:
        mk_parser = lambda t: PostlabelPipeline(learner_attach=t.attach.payload,
                                                learner_label=t.label.payload,
                                                decoder=decoder)
    if settings.intra is not None:
        mk_parser = _mk_intra(mk_parser, settings.intra)

    return ParserConfig(key=decoder_key,
                        decoder=decoder,
                        payload=mk_parser,
                        settings=settings)


def _mk_evaluations():
    """
    Some things we're trying to capture here:

    * some (fancy) learners are parameterised by decoders

    Suppose we have decoders (local, mst, astar) and the learners
    (maxent, struct-perceptron), the idea is that we would want
    to be able to generate the models:

        maxent (no parameterisation with decoders)
        struct-perceptron-mst
        struct-perceptron-astar

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

def _evaluations():
    "the evaluations we want to run"
    ipairs = list(itr.product(_LOCAL_LEARNERS, _INTRA_INTER_CONFIGS))
    res = concat_l([
        concat_l(_core_parsers(l) for l in _LOCAL_LEARNERS),
        concat_l(_mk_basic_intras(l, x) for l, x in ipairs),
        concat_l(_mk_sorc_intras(l, x) for l, x in ipairs),
        concat_l(_mk_dorc_intras(l, x) for l, x in ipairs),
        concat_l(_mk_last_intras(l, x) for l, x in ipairs),
    ])
    return [x for x in res if not _is_junk(x)]


EVALUATIONS = _evaluations()


"""Learners and decoders that are associated with each other.
The idea her is that if multiple decoders have a learner in
common, we will avoid rebuilding the model associated with
that learner.  For the most part we just want the cartesian
product, but some more sophisticated learners depend on the
their decoder, and cannot be shared
"""


GRAPH_DOCS = [
    'wsj_1184.out',
    'wsj_1120.out',
    ]
"""Just the documents that you want to graph.
Set to None to graph everything
"""

DETAILED_EVALUATIONS = [e for e in EVALUATIONS if
                        'maxent' in e.learner.key and
                        ('mst' in e.parser.key or 'astar' in e.parser.key)
                        and 'jnt' in e.settings.key
                        and 'orc' not in e.settings.key]
"""
Any evalutions that we'd like full reports and graphs for.
You could just set this to EVALUATIONS, but this sort of
thing (mostly the graphs) takes time and space to build

HINT: set to empty list for no graphs whatsoever
"""


def print_evaluations():
    """
    Print out the name of each evaluation in our config
    """
    for econf in EVALUATIONS:
        print(econf)
        print()
    print("\n".join(econf.key for econf in EVALUATIONS))

if __name__ == '__main__':
    print_evaluations()
