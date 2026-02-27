# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for origin_conversation_mcp.__main__."""
import os
import sys

import pytest

from origin_conversation_mcp import __main__ as main


def test_env_port_valid():
    assert main._env_port("MCP_PORT", 8000) == 8000
    os.environ["MCP_PORT"] = "9000"
    try:
        assert main._env_port("MCP_PORT", 8000) == 9000
    finally:
        os.environ.pop("MCP_PORT", None)


def test_env_port_invalid_returns_default():
    os.environ["MCP_PORT"] = "not_a_number"
    try:
        assert main._env_port("MCP_PORT", 8000) == 8000
    finally:
        os.environ.pop("MCP_PORT", None)


def test_env_port_empty_returns_default():
    os.environ["MCP_PORT"] = ""
    try:
        assert main._env_port("MCP_PORT", 8000) == 8000
    finally:
        os.environ.pop("MCP_PORT", None)


def test_parse_args_default(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["origin-conversation-mcp"])
    os.environ.pop("MCP_PORT", None)
    os.environ.pop("MCP_HOST", None)
    args = main._parse_args()
    assert args.sse is False
    assert args.port == 8000
    assert args.host == "127.0.0.1"


def test_parse_args_sse(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["origin-conversation-mcp", "--sse"])
    args = main._parse_args()
    assert args.sse is True
    assert hasattr(args, "port")
    assert hasattr(args, "host")
