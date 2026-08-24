# WorkBuddy runtime replay — 2026-08-24

## Classification

`observed-failure`: the project-local activation seam is available, but the
real WorkBuddy UI did not submit the task-agnostic activation request, so no
product activation occurred.

## Environment and setup

- App: WorkBuddy `v5.3.14` (`com.workbuddy.workbuddy`), already running.
- A fresh `新建任务` session was opened instead of reusing the old Feishu
  knowledge-base conversation.
- The workspace picker was checked and the local folder
  `/Users/bilibili/Documents/workspace/github/jununfly/ZAgenticOPN` was opened.
- Model selection was changed from `Auto` to `GLM-5.3` to rule out the
  unselected-model path.
- The intended visible request was `检查 shared context`.

## Observed UI behavior

1. `set_value` displayed the exact request in the composer, but clicking the
   send button through the accessibility element, coordinate click, Return,
   Cmd+Return, and Ctrl+Return did not create a user message or start a run.
2. Direct `type_text` could enter ASCII text, but dropped the first Chinese
   character when asked to enter `检查`; this is not equivalent to the fixed
   Human action script and was not submitted as evidence of a pass.
3. Clicking the `Agent 应用` scene shortcut caused the visible error:
   `Failed to execute 'removeChild' on 'Node': The node to be removed is not a child of this node.`
   The app exposed `重置输入框`, after which the composer recovered.
4. The composer continued to show the request, but the send action remained
   non-submitting. No WorkBuddy response, shell execution, or structured
   handoff appeared.

## Store check

After the UI replay, the project-local store was queried read-only:

```text
sqlite3 .zagenticopn/shared.sqlite3 \
  "SELECT type, scope, work_id, agent_id, activation_id, created_at
   FROM events WHERE scope = 'zagenticopn/experience-version';"
```

Result: no rows. The store still contains only the older
`jununfly/ZAgentic/zj-research-report` publish/discover events; no new
`zagenticopn/experience-version` `discover` or `claim` event was produced.

## Decision boundary

This replay does not invalidate the project-local `scripts/activate_agent.py`
subprocess evidence. It shows that the real WorkBuddy v5.3.14 UI/runtime is
still not wired to invoke that seam. The roadmap node remains `in_progress`;
the three consecutive real value experiments have not started.
