# Comment preparation

After the review agent has finished validating findings, give a separate agent
accepted.json from `build-report.py prepare`. Read `schemas/comments.schema.json`.
Return one concise editable comment per accepted finding, linked by finding_id.
Describe the concrete failure, its trigger and impact, and an actionable remedy.
Include replacement code only when supported by the supplied evidence.

Preserve accepted findings. If evidence is insufficient to write an accurate
comment, return the issue to the reviewer for correction before building.
Do not generate HTML, CSS, JavaScript, GitHub request payloads, metadata,
source excerpts, or duplicate findings. The renderer and helper construct
submission payloads from the user's selected comments and actions.
