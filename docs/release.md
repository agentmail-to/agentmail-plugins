# Plugin release procedure

This is the canonical release procedure for the AgentMail plugin on Claude Code,
Codex, and Cursor. It is contract-driven and intentionally does not encode a
specific release number, commit, or tool inventory.

## Decide whether to release

Release the plugin when its packaged skills, MCP configuration, metadata, client
compatibility, or user-facing behavior changes. An AgentMail MCP release requires
a plugin release only when it changes the public contract, authentication,
permissions, or a workflow described by a bundled skill.

Use the generated MCP manifest and canonical skills repository as inputs. Do not
copy tool lists from prose documentation or edit `skills/` directly.

## Prepare the release

1. In `agentmail-skills`, synchronize from the released `agentmail-mcp` checkout,
   review the reported contract changes, and merge the canonical skill updates.
2. Export the merged canonical skills into this repository:

   ```bash
   python3 /path/to/agentmail-skills/scripts/skills.py build \
     --target /path/to/agentmail-plugins
   ```

3. Choose the next plugin version according to the compatibility impact. Apply
   the same version to every package manifest. Never use a version as a proxy for
   the MCP server version; they have independent release cadences.
4. Update `CHANGELOG.md` with the packaged behavior change and migration notes.
5. Refresh `compatibility.json` against the published SDK, CLI, and toolkit
   versions exercised by the bundled instructions.
6. Update installation, upgrade, authentication, and capability copy when those
   behaviors changed. Keep the marketplace description synchronized with the
   package manifests.

## Validate the package

Run the local checks:

```bash
python3 scripts/validate_repo.py
python3 scripts/check_compatibility.py
claude plugin validate . --strict
```

The marketplace workflow must also prove that:

- the current `agentmail-mcp` manifest matches the canonical skills contract;
- the plugin's complete `skills/` tree is the generated export of
  `agentmail-skills`;
- Codex can add the repository marketplace and install the plugin;
- Claude Code accepts both the marketplace and plugin manifests.

Do not publish when a generated-tree or upstream-contract check is failing. Fix
the canonical source and regenerate instead of patching a downstream copy.

## Test clean install and upgrade

Test both a clean installation and an upgrade from the previously published
version in all three clients. Record the plugin commit, client version, and result
in the release pull request or release issue.

For each client:

1. Install or upgrade through the supported marketplace path.
2. Reload plugins or start a new session so cached package content cannot mask the
   result.
3. Complete the hosted MCP OAuth flow.
4. Confirm the advertised tool catalog matches the released manifest.
5. Invoke a representative read-only tool for basic connectivity and a read-only
   tool from each changed capability. Verify returned data and error handling.
6. Confirm changed skills are discoverable and contain the released instructions.

Release acceptance must not send mail, create or delete inboxes, mutate messages,
connect accounts, or invoke any tool whose manifest annotations do not mark it
read-only. Schema and discovery inspection is sufficient when a changed
capability has no read-only operation.

### Claude Code

Verify both installation and the existing-user update path:

```bash
claude plugin marketplace update agentmail
claude plugin update agentmail@agentmail
```

Apply the new package with `/reload-plugins` or a new session. The manifest
version must change whenever packaged content changes because Claude Code uses it
to determine update availability.

### Codex

Verify both installation and marketplace refresh:

```bash
codex plugin marketplace add agentmail-to/agentmail-plugins
codex plugin marketplace upgrade agentmail
codex plugin add agentmail@agentmail
```

Use a clean `CODEX_HOME` for the clean-install test and a previously installed
copy for the upgrade test. Start a new session after each test installation.

### Cursor

Test the repository locally from Cursor's local plugin directory before submitting
the public update. Confirm every component loads and OAuth succeeds.

Update the existing AgentMail listing in the Cursor publisher dashboard to the
released repository commit. Do not create a new listing. Submit once, record the
review state, and wait if the update is pending; each public update is reviewed.

After approval, verify the public listing from this repository checkout:

```bash
python3 scripts/check_cursor_marketplace.py
```

The check derives its expected commit, description, and skill inventory from the
checkout, so it remains valid for future releases. Do not mark the release
complete until it passes.

## Complete the release

The release is complete when:

- repository and cross-repository checks pass;
- clean-install and upgrade acceptance is recorded for all three clients;
- the Cursor listing is approved and its live revision check passes;
- affected AgentMail documentation is published; and
- rollback remains possible by restoring the previous plugin revision or listing
  commit.

Do not delete or recreate marketplace listings as a rollback mechanism. Restore a
known-good revision and follow the marketplace's normal review process.

## Vendor references

Check these live references before changing packaging or update commands:

- [Claude Code: install and manage plugins](https://code.claude.com/docs/en/discover-plugins)
- [Claude Code: plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- [Codex: package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Cursor: plugins](https://cursor.com/docs/plugins)
- [Cursor: plugin reference](https://cursor.com/docs/reference/plugins)
- [Cursor: marketplace security and update review](https://cursor.com/help/security-and-privacy/marketplace-security)
