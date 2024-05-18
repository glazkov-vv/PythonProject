from __future__ import annotations
import asyncio
import os
import shutil
from typing import *
from logic.permissions import FilePermissions
from logic.selection import Selection
from logic.workspacemanager import WorkspaceManager


class Transaction:
    def __init__(self) -> None:
        pass

    async def execute(self, progress_callback: None | Callable = None) -> None | str:
        raise NotImplementedError()

    def revert(self) -> Transaction:
        raise NotImplementedError()

    @staticmethod
    def reports_progress() -> bool:
        return False


def calc_size(path: str) -> int:
    if (not os.path.exists(path)):
        return 0
    if (not os.path.isdir(path)):
        return os.path.getsize(path)
    ans = 0
    for h in os.walk(path):
        for hh in h[1]+h[2]:
            ans += os.path.getsize(os.path.join(h[0], hh))
    return ans


def calc_total_size(paths: Iterable[str]) -> int:
    sum = 0
    for h in paths:
        sum += calc_size(h)
    return sum


class DoNothingTransaction(Transaction):
    def __init__(self) -> None:
        super().__init__()

    async def execute(self) -> None | str:
        pass

    def revert(self) -> Transaction:
        return DoNothingTransaction()
