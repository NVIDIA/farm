# nvctmock

a really lame mock of the nvct api, less any authentication bits, which should be just enough to get ov farm to sent tasks so we can profile the nvct controller in ov farm.

## ov farm configuration changes

Add the following to your local farm config toml which overrides our farm defaults:

```toml
[settings.nv.svc.farm.controller]
bay_controller_class = "nv.svc.farm.services.controller.facilities.bays.MultiSlotBay"
bay_controller_args.max_capacity = 1500 # max number of tasks to submit to nvctmock at once
job_manager_class = "nv.svc.farm.services.jobs.facilities.manager.nvct.NVCTProcessManager"
job_manager_args.disable_authn = true
job_manager_args.api_endpoint = "http://localhost:8877/v1/nvct/tasks"
job_manager_args.username = "junk"
job_manager_args.password = "junk"
```

Be sure to run ov farm with your configuration.

## add `create-render` to the ov farm container:

Add the `create-render` job definition:

```Dockerfile
USER nvs # the user in the nv.svc.farm container may be different
COPY --chown=nvs:nvs ./job.omni.farm.render.kit /home/nvs/.local/share/nv-svc-farm/job-definitions/create-render.kit
```

## adding pyinstrument (optional)

Add `pyinstrument` to `pyproject.toml`:

```toml
# pyinstrument
pyinstrument = "5.0.0"
```

.. then run `make freeze` to get tox to bake all that into your `poetry.lock` file.

Modify the `Dockerfile` entrypoint to run the farm using the profiler:

```Dockerfile
ENTRYPOINT  ["python", "-c", "from pyinstrument import Profiler; import nv.svc.farm.standalone; prof = Profiler(async_mode='enabled'); prof.start();\ntry: nv.svc.farm.standalone.main();\nfinally: prof.stop(); prof.write_html('/tmp/profile.html')"]
```

## ov farm docker hints

run the ov farm services in docker with host networking so it can access the `nvctmock` service running on localhost:

```shell
docker run --network=host -it {image hash}
```

## building and running nvctmock

It's zero config ...

```shell
go build
./nvctmock
```

On startup you'll see:
```json
{"time":"2025-01-24T11:45:13.513448861-08:00","level":"INFO","msg":"waiting for connections","listen_addr":":8877"}
```

## a stupid-simple example session using curl

Create a new task:

```shell
curl -d {} -v http://localhost:8877/v1/nvct/tasks
* Host localhost:8877 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8877...
* Connected to localhost (::1) port 8877
> POST /v1/nvct/tasks HTTP/1.1
> Host: localhost:8877
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Length: 2
> Content-Type: application/x-www-form-urlencoded
>
< HTTP/1.1 200 OK
< Date: Thu, 16 Jan 2025 19:05:22 GMT
< Content-Length: 56
< Content-Type: text/plain; charset=utf-8
<
* Connection #0 to host localhost left intact
{"task":{"id":"1","status":"Submitted","healthInfo":{}}}%
```

Retrieve task info:

```shell
curl -v http://localhost:8877/v1/nvct/tasks/1
* Host localhost:8877 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8877...
* Connected to localhost (::1) port 8877
> GET /v1/nvct/tasks/1 HTTP/1.1
> Host: localhost:8877
> User-Agent: curl/8.5.0
> Accept: */*
>
< HTTP/1.1 200 OK
< Date: Thu, 16 Jan 2025 19:05:45 GMT
< Content-Length: 56
< Content-Type: text/plain; charset=utf-8
<
* Connection #0 to host localhost left intact
{"task":{"id":"1","status":"Submitted","healthInfo":{}}}%
```

## building farm with nvct mock

Create the farm k8s cluster locally with ingress using an interactive controller container connected to nvct mock service.

```bash
devspace create
devspace dev -p nginx -p nvct-mock -p controller
```

After the cluster is ready, start the controller service from the dev container.

```bash
make start svc=controller-svc
```
