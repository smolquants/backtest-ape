import click
import backtest_ape

from ape import networks
from ast import literal_eval
from time import time
from typing_inspect import get_origin


def main():
    """
    Main backtester script.
    """
    # echo provider setup
    ecosystem_name = networks.provider.network.ecosystem.name
    network_name = networks.provider.network.name
    provider_name = networks.provider.name
    connection_name = f"{ecosystem_name}:{network_name}:{provider_name}"
    click.echo(f"You are connected to provider network {connection_name}.")

    # fail if not mainnet-fork
    if network_name != "mainnet-fork":
        raise ValueError("not connected to mainnet-fork.")

    # prompt user which backtest runner to use
    runner_cls_name = click.prompt(
        "Runner type", type=click.Choice(backtest_ape.__all__, case_sensitive=False)
    )
    runner_cls = getattr(backtest_ape, runner_cls_name)

    # prompt user for fields on runner to init with
    kwargs = {}
    for name, field in runner_cls.__fields__.items():
        # default to str if not base type
        type_origin = get_origin(field.annotation)
        type_ = field.annotation if type_origin is None else str
        value = click.prompt(
            f"Runner kwarg ({name})", default=field.default, type=type_
        )

        # parse field value from str if not base type
        if type_origin is not None:
            value = literal_eval(value)

        kwargs[name] = value

    # setup runner
    runner = runner_cls(**kwargs)
    runner.setup()

    # run backtest
    # TODO: choice for back or forward testing
    path = f"scripts/results/{runner_cls_name}-{int(time())}.csv"
    start = click.prompt("Start block number", type=int)
    stop = click.prompt("Stop block number", type=int, default=-1)
    if stop < 0:
        stop = None

    runner.backtest(path, start, stop)
