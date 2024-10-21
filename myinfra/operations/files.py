from pathlib import Path
from pyinfra import host
from pyinfra.api import operation, exceptions
from pyinfra.api.command import QuoteString, StringCommand
from pyinfra.operations import files
from pyinfra.facts import files as file_facts

from . import archive
from ..facts import checksum as checksum_facts


@operation()
def copy(
    src,
    dest,
    present=True,
    user=None,
    group=None,
    mode=None,
    add_deploy_dir=True,
    create_remote_dir=True,
    force=False,
    assume_exists=False,
):
    if present:
        yield from files.put._inner(
            src,
            dest,
            user=user,
            group=group,
            mode=mode,
            add_deploy_dir=add_deploy_dir,
            create_remote_dir=create_remote_dir,
            force=force,
            assume_exists=assume_exists,
        )
    else:
        yield from files.file._inner(
            dest,
            present=False,
        )


@operation()
def template(
    src,
    dest,
    present=True,
    user=None,
    group=None,
    mode=None,
    create_remote_dir=True,
    jinja_env_kwargs=None,
    **data,
):
    jinja_env_kwargs = {"trim_blocks": True, **(jinja_env_kwargs or {})}

    if present:
        yield from files.template._inner(
            src,
            dest,
            user=user,
            group=group,
            mode=mode,
            create_remote_dir=create_remote_dir,
            jinja_env_kwargs=jinja_env_kwargs,
            **data,
        )
    else:
        yield from files.file._inner(
            dest,
            present=False,
        )


@operation()
def download(src, dest, src_dir=None, sha256sum=None, present=True, mode=None):
    if present:
        info = host.get_fact(file_facts.File, path=dest)
        if info is not None and sha256sum is not None:
            cur_sha256sum = host.get_fact(checksum_facts.SHA256Sum, path=dest)
            if cur_sha256sum != sha256sum:
                yield from files.file._inner(path=dest, present=False)

                info = host.get_fact(file_facts.File, path=dest)

        if info is None:
            temp_dir = Path(host._get_temp_directory())

            yield from files.download._inner(
                src=src,
                dest=str(temp_dir / Path(src).name),
            )

            if src.endswith(".tar.gz"):
                yield from archive.untar._inner(path=str(temp_dir / Path(src).name))
            elif src.endswith(".tar.bz2"):
                yield from archive.untar._inner(
                    path=str(temp_dir / Path(src).name), flags="j"
                )
            elif src.endswith(".zip"):
                yield from archive.unzip._inner(path=str(temp_dir / Path(src).name))
            else:
                raise exceptions.OperationError(f"Unsupported file type in {src}.")

            yield from files.file._inner(
                path=str(temp_dir / Path(src).name), present=False
            )

            yield StringCommand(
                "mv",
                QuoteString(str(temp_dir / (src_dir or "") / Path(dest).name)),
                QuoteString(str(Path(dest).parent)),
            )

            if src_dir:
                yield from files.directory._inner(
                    path=str(temp_dir / src_dir), present=False
                )

    yield from files.file._inner(path=dest, present=present, mode=mode)
