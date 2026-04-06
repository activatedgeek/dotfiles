from pyinfra.api import config

mac = (
    [
        (
            "@local",
            dict(),
        )
    ],
    dict(),
)

all = (
    [h for h, _ in mac[0]],
    dict(
        ## Latest binary versions
        binary_versions=config.BINARY_VERSIONS,
    ),
)
