"""Manage registration of LaunchAgents in the current user's GUI domain."""

from pathlib import PurePosixPath
from shlex import quote

from pyinfra.api import operation
from pyinfra.api.command import QuoteString, StringCommand
from pyinfra.facts.launchd import LaunchdStatus
from pyinfra.facts.server import Home
from pyinfra.operations import files

from pyinfra import host

from . import files as myfiles


@operation()
def plist(service, src, present=True, mode=600, **data):
    """Template and register a GUI LaunchAgent, or unregister and remove it.

    + service: label declared in the template
    + src: local Jinja template path, relative to the deploy directory
    + present: whether the plist and agent should exist
    + mode: plist permissions (defaults to 600)
    + data: template variables

    Changed templates reload the agent. Removal unregisters the agent before
    deleting its plist, preserving the shared LaunchAgents directory.
    The destination is ``~/Library/LaunchAgents/<service>.plist`` on the host.
    Parent directories for ``stdout_path`` and ``stderr_path`` template variables
    are created with mode 700. Log files and directories are preserved on removal.
    """
    remote_home = host.get_fact(Home)
    dest = f"{remote_home}/Library/LaunchAgents/{service}.plist"

    if not present:
        yield from agent._inner(service=service, plist_path=dest, present=False)
        yield from files.file._inner(path=dest, present=False)
        return

    log_dirs = {str(PurePosixPath(data[key]).parent) for key in ("stdout_path", "stderr_path") if data.get(key)}
    for log_dir in sorted(log_dirs):
        yield from files.directory._inner(path=log_dir, mode=700)

    changed = False
    for command in myfiles.template._inner(src=src, dest=dest, mode=mode, **data):
        changed = True
        yield command

    yield from agent._inner(service=service, plist_path=dest, reloaded=changed)


@operation()
def agent(service, plist_path, present=True, reloaded=False):
    """Ensure a LaunchAgent is registered, independently of its process state.

    + service: label declared in the plist
    + plist_path: absolute path to an installed plist, managed separately
    + present: whether the agent should be registered
    + reloaded: reload an existing agent; accepts a callable such as a template
      operation's ``did_change`` method, evaluated during execution

    Install the plist before this operation. For removal, call this operation
    before deleting the plist. The execution user must have a GUI login session;
    this operation does not manage system LaunchDaemons or other users' agents.
    Registration does not force an immediate run (the plist's triggers apply).
    The plist's parent directory is ensured with mode 700 when present and is
    preserved on removal because other agents may share it.
    """
    loaded = service in host.get_fact(LaunchdStatus)
    service_target = f'"gui/$(id -u)/"{quote(service)}'

    if not present:
        if loaded:
            yield StringCommand("launchctl bootout", service_target)
        return

    yield from files.directory._inner(path=str(PurePosixPath(plist_path).parent), mode=700)

    reload_requested = reloaded() if callable(reloaded) else reloaded
    if loaded and not reload_requested:
        return

    # Validate before unloading so a malformed replacement leaves the job loaded.
    yield StringCommand("plutil -lint", QuoteString(plist_path))
    if loaded:
        yield StringCommand("launchctl bootout", service_target)
    yield StringCommand("launchctl bootstrap", '"gui/$(id -u)"', QuoteString(plist_path))
