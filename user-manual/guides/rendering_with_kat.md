# Using Farm to Render Kit Applications

The `create-render` job definition can be used to render a USD stage using any Omniverse Kit application, such as USD Composer, as long as the appropriate extensions are installed. This includes custom Kit applications built using the [Kit Application Template](https://github.com/NVIDIA-Omniverse/kit-app-template).

The `create-render` job definition is contained within `job.omni.farm.render.kit` and must be installed manually for Standalone and Kubernetes deployments.

In order for Farm Agents to be able to successfully launch `create-render` job tasks, the job definition must be configured with an accessible path to the startup script of your Kit application. The application can be installed locally or via a network mount, as long the Farm Agent can access it in a consistent fashion.

## Requirements

- Farm Queue running locally or network accessible

- One or more Farm Agents

  - Running on systems with an NVIDIA GPU

  - Connected to the Farm Queue

  - With access to:

    - a properly configured `create-render` job definition.

    - the Kit application to launch for rendering.

    - all data required by the USD scenes being rendered

## Modifying the `create-render` Job Definition

To have the agent use your manually installed Kit application, set the `command` option in the `[job.create-render]` section of the Kit file to point to the absolute path of the startup script.

Use single-quotes (''), rather than double-quotes ("") when specifying the path to avoid having to escape characters in the path: `command = 'C:\\Program Files\\my_app\\my_usd_composer.kit.bat'` `command = '/opt/my_app/my.usd_composer.kit.sh'`

`job.omni.farm.render.kit</resources/job.omni.farm.render.kit>`

You must update the `command` parameter on **(line 37)** to be a full valid path to your Kit application.

## Adding the Updated Job Definition

Depending on how job definitions are being managed within your Farm instance, this may require modifying a locally accessible job definition file or uploading to a remote job store.

### Local DirectoryJobStore

Job definitions are stored in a local directory and may be \"manually\" managed.

### RemoteJobStore

Job definitions are managed by the `jobs` service. Job definitions are uploaded by calling the `/queue/management/jobs/save` endpoint.

The python script `job_definition_upload.py </resources/job_definition_upload.py>` can be used to simplify this:

``` shell
python job_definition_upload.py job.omni.farm.render.kit --farm-url http://localhost:8222 --api-key change-me
```

You must specify:

- the path to the updated `create-render.kit` file.

- the URL of *your* Farm instance.

- a valid `api-key`.

This is discussed in greater detail within the `/guides/job_stores` guide.

## Errors

Failure to update the `create-render` job definition results in an error when starting the tasks on a Farm Agent. This will appear as an error in the Task's logs:

``` text
ERROR: Farm Agent could not find a "C:\users\Username\src\kit-app-template\windows_x86_64\release\my-app.usd_composer.kit.bat" command to execute. Additional information from the host are listed below:

<class 'FileNotFoundError'>: [WinError 2] The system cannot find the file specified
```

Other indicators of an issue with the `create-render` job definition:

- It is not listed in the Dashboard under the `DEFINITIONS` tab or with any agents in the `AGENTS` tab.

- There is an error message in the `jobs` or `controller` service error logs.

## Rendering with Different Kit Applications

A job definition contains a single `command` parameter, so in cases where you have multiple Kit applications that you want to use for rendering, you have two options:

- Have one job definition that calls a Kit application capable of rendering all scenes.

- Use the `create-render` job definition as a template to create alternatives, updating the job definition name and command for each kit application you want to use for rendering. These can be in separate `.kit` files or all in the same one.

The `Movie Capture` Kit extension, used to submit render tasks to a Farm instance, allows you to specify alternative job definitions in `Queue Settings`, `Job Types`.
