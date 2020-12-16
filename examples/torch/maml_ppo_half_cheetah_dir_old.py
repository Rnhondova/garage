#!/usr/bin/env python3
"""This is an example to train MAML-VPG on HalfCheetahDirEnv environment."""
from copy import deepcopy

# pylint: disable=no-value-for-parameter
import click
import torch

from garage import wrap_experiment
from garage.envs import normalize
from garage.envs.base import GarageEnv
from garage.envs.mujoco.half_cheetah_dir_env2 import HalfCheetahDirEnv
from garage.experiment import LocalRunner, MetaEvaluator
from garage.experiment.deterministic import set_seed
from garage.experiment.task_sampler import EnvPoolSampler
from garage.np.baselines import LinearFeatureBaseline
from garage.torch.algos import MAMLPPO
from garage.torch.policies import GaussianMLPPolicy


@click.command()
@click.option('--seed', default=1)
@click.option('--epochs', default=300)
@click.option('--rollouts_per_task', default=40)
@click.option('--meta_batch_size', default=20)
@wrap_experiment(snapshot_mode='all')
def maml_ppo(ctxt, seed, epochs, rollouts_per_task, meta_batch_size):
    """Set up environment and algorithm and run the task.

    Args:
        ctxt (garage.experiment.ExperimentContext): The experiment
            configuration used by LocalRunner to create the snapshotter.
        seed (int): Used to seed the random number generator to produce
            determinism.
        epochs (int): Number of training epochs.
        rollouts_per_task (int): Number of rollouts per epoch per task
            for training.
        meta_batch_size (int): Number of tasks sampled per batch.

    """
    set_seed(seed)
    env = GarageEnv(normalize(HalfCheetahDirEnv(), expected_action_scale=10.))
    forward_env = deepcopy(env)
    backward_env = deepcopy(env)
    forward_env.set_task({'direction': 1.})
    backward_env.set_task({'direction': -1.})
    test_task_sampler = EnvPoolSampler([forward_env, backward_env])

    policy = GaussianMLPPolicy(
        env_spec=env.spec,
        hidden_sizes=(64, 64),
        hidden_nonlinearity=torch.tanh,
        output_nonlinearity=None,
    )

    baseline = LinearFeatureBaseline(env_spec=env.spec)

    max_path_length = 100

    meta_evaluator = MetaEvaluator(test_task_sampler=test_task_sampler,
                                   max_path_length=max_path_length,
                                   n_test_tasks=2,
                                   n_test_rollouts=10)

    runner = LocalRunner(ctxt)
    algo = MAMLPPO(env=env,
                   policy=policy,
                   baseline=baseline,
                   max_path_length=max_path_length,
                   meta_batch_size=meta_batch_size,
                   discount=0.99,
                   gae_lambda=1.,
                   inner_lr=0.1,
                   num_grad_updates=1,
                   meta_evaluator=meta_evaluator)

    runner.setup(algo, env)
    runner.train(n_epochs=epochs,
                 batch_size=rollouts_per_task * max_path_length)


maml_ppo()