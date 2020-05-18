#Modified by: David Esteban Imbajoa ruiz 2020
#imbajoaruiz.1922212@studenti.uniroma1.it

import shutil
from pathlib import Path

import gym
import numpy as np
import pythomata
from gym.spaces import MultiDiscrete
from gym.wrappers import Monitor
from gym_breakout_pygame2.breakout_env import BreakoutConfiguration
from pythomata.dfa import DFA
from temprl.wrapper import TemporalGoalWrapper, TemporalGoal

from breakout.common import BreakoutWrapper, extract_breakout_fluents
from rl_algorithm.brains import Sarsa, QLearning
from rl_algorithm.callbacks import ModelCheckpoint, plot_history
from rl_algorithm.core import Agent, TrainEpisodeLogger
from rl_algorithm.policies import EpsGreedyQPolicy, AutomataPolicy
from rl_algorithm.temporal import TemporalGoalWrapperLogTraces

class BreakoutLearnerWrapper(gym.Wrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(BreakoutWrapper(*args, **kwargs))

        self.observation_space = MultiDiscrete((
            self.env.observation_space.spaces["paddle_x"].n,
            self.env.observation_space.spaces["ball_x"].n,
            self.env.observation_space.spaces["ball_y"].n,
            self.env.observation_space.spaces["ball_x_speed"].n,
            self.env.observation_space.spaces["ball_y_speed"].n
        ))


def make_env_from_dfa(config: BreakoutConfiguration, dfa: DFA,
                      goal_reward: float = 1000.0,  reward_shaping: bool = True, output_dir=None) -> gym.Env:
    """
    Make the Breakout environment.

    :param config: the Breakout configuration.
    :param dfa: the automaton that constitutes the goal.
    :param goal_reward: the reward associated to the goal.
    :param reward_shaping: apply automata-based reward shaping.
    :return: the Gym environment.
    """
    unwrapped_env = BreakoutLearnerWrapper(config)

    tg = TemporalGoal(automaton=dfa,
                      reward=goal_reward,
                      reward_shaping=reward_shaping,
                      zero_terminal_state=False,
                      extract_fluents=extract_breakout_fluents)

    env = TemporalGoalWrapper(
        unwrapped_env,
        [tg],
        combine=lambda obs, qs: tuple((*obs, *qs)),
        feature_extractor=(lambda obs, action: (
            obs["paddle_x"],
            obs["ball_x"],
            obs["ball_y"],
            obs["ball_x_speed"],
            obs["ball_y_speed"],
        ))
    )
    if(output_dir is not None):
        positive_traces_path = Path(output_dir, "learner_positive_traces.txt")
        negative_traces_path = Path(output_dir, "learner_negative_traces.txt")
        env = TemporalGoalWrapperLogTraces(env, extract_breakout_fluents, positive_traces_path, negative_traces_path)
    return env


def run_learner(arguments, configuration, dfa: pythomata.dfa.DFA):
    agent_dir = Path(arguments.output_dir) / "learner"
    shutil.rmtree(agent_dir, ignore_errors=True)
    agent_dir.mkdir(parents=True, exist_ok=False)

        #case
    if arguments.case==1:
        ball_enabled_=True
        fire_enabled_=False
        output_dir_=None
        secondlearner_=True
    else:
        ball_enabled_=True
        fire_enabled_=False
        output_dir_=arguments.output_dir
        secondlearner_=False

    config = BreakoutConfiguration(brick_rows=arguments.rows, brick_cols=arguments.cols,
                                   brick_reward=arguments.brick_reward, step_reward=arguments.step_reward,
                                   fire_enabled=fire_enabled_, ball_enabled=ball_enabled_,secondlearner=secondlearner_)
    env = make_env_from_dfa(config, dfa,output_dir=output_dir_)

    np.random.seed(arguments.seed)
    env.seed(arguments.seed)

    policy = AutomataPolicy((-1, ), nb_steps=configuration.nb_exploration_steps, value_max=0.8, value_min=configuration.min_eps)

    algorithm = Sarsa if configuration.algorithm == "sarsa" else QLearning
    agent = Agent(algorithm(None,
                            env.action_space,
                            gamma=configuration.gamma,
                            alpha=configuration.alpha,
                            lambda_=configuration.lambda_),
                  policy=policy,
                  test_policy=EpsGreedyQPolicy(eps=0.001))

    history = agent.fit(
        env,
        nb_steps=configuration.nb_steps,
        visualize=configuration.visualize_training,
        callbacks=[
            ModelCheckpoint(str(agent_dir / "checkpoints" / "agent-{}.pkl")),
            TrainEpisodeLogger()
        ]
    )

    history.save(agent_dir / "history.json")
    agent.save(agent_dir / "checkpoints" / "agent.pkl")
    plot_history(history, agent_dir)

    agent = Agent.load(agent_dir / "checkpoints" / "agent.pkl")
    agent.test(Monitor(env, agent_dir / "videos"), nb_episodes=10, visualize=True)

    env.close()
