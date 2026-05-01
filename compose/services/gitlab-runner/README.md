### Enabling Registry Caching

A [registry cache backend](https://docs.docker.com/build/cache/backends/registry/) significantly reduces built time by keeping
cached layers for any docker builds. To enable, modify the docker configuration
at `/etc/docker/daemon.json`,
```json
    ...
    "features": {
        "containerd-snapshotter": true
    },
    ...
```

Restart docker as,
```shell
sudo systemctl restart docker
```

The `--cache-to` and `--cache-from` should be able to point to external registry.

**WARNING**: Changing this configuration will completely wipe out existing containers and volumes.

### Using GPU Runners

To enable access to GPUs for each job of Gitlab runner, the easiest
workaround is to change the default runtime of the underlying docker daemon.
Modify the `/etc/docker/daemon.json` to,
```json
    ...
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    },
    ...
```

Restart docker as,
```shell
sudo systemctl restart docker
```
