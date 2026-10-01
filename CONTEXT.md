# PR Review Reports

PR review reports combine source-level findings with the pull request's review state and discussion so a reviewer can understand both the code and the conversation around it.

## Language

**PR lifecycle state**:
Whether a pull request is open, closed, or merged. This is independent of reviewers' decisions.
_Avoid_: Review status

**Review decision**:
The aggregate decision reviewers have recorded for the pull request, such as approved or changes requested. It is independent of whether the pull request is open, closed, or merged.
_Avoid_: PR lifecycle state

**PR discussion**:
The feedback attached to a pull request: general conversation comments, review summaries, and inline review threads with their replies and resolution state.
_Avoid_: Findings

**Finding**:
An actionable issue identified by the code review, linked to the changed source. Findings are distinct from existing PR discussion.
_Avoid_: PR comment
