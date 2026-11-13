# Wayfinder tracker (local markdown)

This repo has no issue tracker configured for wayfinding, so maps and tickets live here as markdown files.

- **Map**: `map.md` (label `wayfinder:map`).
- **Tickets**: `tickets/NNN-slug.md`, children of the map. The `NNN` prefix is the ticket's id.
- **Front matter** on each ticket:
  - `title`: the ticket's name. Always refer to a ticket by this, not by its id.
  - `type`: `research` | `prototype` | `grilling` | `task` (the `wayfinder:<type>` label).
  - `status`: `open` | `closed`.
  - `assignee`: empty = unclaimed. A session claims a ticket by filling this in before doing any work.
  - `blocked_by`: list of ticket ids. This tracker has no native dependencies, so this field stands in for them.
- **Frontier**: tickets that are `open`, have no `assignee`, and whose `blocked_by` tickets are all `closed`.
- **Resolution**: append a `## Resolution` section to the ticket, set `status: closed`, and add a one-line pointer to the map's "Decisions so far".
