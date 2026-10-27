"""Plugin de testes: troca o `ProcessPoolExecutor` pelo `ThreadPoolExecutor`.

Alguns ambientes (sandboxes, CI restritos) não deixam criar os semáforos de que os
processos precisam (`PermissionError`). Os testes correm com threads, sem mudar o código.
"""

from __future__ import annotations

import concurrent.futures
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest


class _ThreadPool(ThreadPoolExecutor):
    """Aceita os argumentos do `ProcessPoolExecutor` que o `ThreadPoolExecutor` não tem."""

    def __init__(self, max_workers=None, mp_context=None, initializer=None, initargs=(), **_):
        super().__init__(max_workers=max_workers, initializer=initializer, initargs=initargs)

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        return super().map(fn, *iterables, timeout=timeout)


@pytest.fixture(autouse=True)
def sem_processos(monkeypatch):
    monkeypatch.setattr(concurrent.futures, "ProcessPoolExecutor", _ThreadPool)
    for name, module in list(sys.modules.items()):
        if name.startswith("leis_portugal") and getattr(module, "ProcessPoolExecutor", None) is not None:
            monkeypatch.setattr(module, "ProcessPoolExecutor", _ThreadPool)
    yield
