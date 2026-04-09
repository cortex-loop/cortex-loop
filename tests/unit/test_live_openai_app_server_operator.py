"""Focused unit tests for the Codex App Server operator harness."""

from __future__ import annotations

from lab.live_openai_app_server_operator import (
    classify_app_server_request_blocker,
    summarize_app_server_timeline,
)


def test_classify_app_server_request_blocker_recognizes_approval_and_input_requests() -> None:
    assert (
        classify_app_server_request_blocker(["item/commandExecution/requestApproval"])
        == "approval_requested"
    )
    assert (
        classify_app_server_request_blocker(["item/tool/requestUserInput"])
        == "user_input_requested"
    )
    assert classify_app_server_request_blocker(["thread/status/changed"]) is None


def test_summarize_app_server_timeline_keeps_lifecycle_counts_and_result_text() -> None:
    timeline = [
        {
            "direction": "receive",
            "kind": "notification",
            "method": "thread/started",
            "payload": {"threadId": "thread_123"},
        },
        {
            "direction": "receive",
            "kind": "notification",
            "method": "item/started",
            "payload": {"item": {"type": "agentMessage"}},
        },
        {
            "direction": "receive",
            "kind": "notification",
            "method": "item/agentMessage/delta",
            "payload": {"delta": "Task is incomplete"},
        },
        {
            "direction": "receive",
            "kind": "notification",
            "method": "item/completed",
            "payload": {"item": {"type": "agentMessage", "text": "Task is incomplete"}},
        },
        {
            "direction": "receive",
            "kind": "request",
            "method": "item/fileChange/requestApproval",
            "payload": {"id": 9},
        },
    ]

    summary = summarize_app_server_timeline(timeline, thread_read={})

    assert summary["thread_id"] == "thread_123"
    assert summary["lifecycle_event_count"] == 4
    assert summary["lifecycle_event_labels"] == [
        "thread/started",
        "item/started",
        "item/agentMessage/delta",
        "item/completed",
    ]
    assert summary["item_lifecycle_counts"] == {"agentMessage": 2}
    assert summary["server_request_methods"] == ["item/fileChange/requestApproval"]
    assert summary["result_text"] == "Task is incomplete"


def test_summarize_app_server_timeline_can_fall_back_to_thread_read_agent_text() -> None:
    summary = summarize_app_server_timeline(
        [],
        thread_read={
            "threadId": "thread_abc",
            "turns": [
                {
                    "items": [
                        {
                            "type": "agentMessage",
                            "text": "Lifecycle proof completed cleanly.",
                        }
                    ]
                }
            ],
        },
    )

    assert summary["thread_id"] == "thread_abc"
    assert summary["result_text"] == "Lifecycle proof completed cleanly."
