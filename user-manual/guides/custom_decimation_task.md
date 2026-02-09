# A Custom Blender Decimation Task

Note: Please ensure that all Farm components are installed and running before continuing.

Farm is more than just a render queue. It can process virtually anything - whether in Omniverse or not. In the next example, we will define a custom job and use Blender to decimate the meshes.

## Example: Using Blender to Decimate Meshes

Now that we've learned how to execute built-in tasks, let's see how to define and run our own custom ones. For this example, we will be using Farm Agent to automate a mesh simplification task in Blender --- which you can download for free from the [Blender](https://blender.org/) website.

As an illustration of typical batch operations you may find in studio or enterprise scenarios, the task will:

1.  Open an OBJ file

2.  Decimate its meshes to a given ratio

3.  Export the scene as a USD asset

While this is a simple scenario, it does demonstrates important concepts:

- No task is too small to benefit from automation.

- Creating custom job types for Farm Agent is a fairly straightforward process.

- Using USD (the 3D industry standard) to facilitate data exchange and interoperability.

### Blender Mesh Decimation Script

Let's start where most automation tasks begin: by running our task locally.

Below is our Python script which will be driving the work to do in Blender. It supports the following arguments:

`--source`

:   The absolute path to the OBJ file to decimate.

`--destination`

:   The absolute path where the resulting USD file will be saved.

`--ratio`

:   An optional parameter between `0.0` and `1.0`, specifying the amount by which meshes should be simplified.

``` python
# File: job.blender-decimate.py

import argparse
import sys
from typing import List

import bpy


class BlenderArgumentParser(argparse.ArgumentParser):
    """Argument parser for Python scripts running in Blender."""

    def _get_arguments_after_double_dash(self) -> List[str]:
        """
        Extract any arguments intended to be passed to Blender scripts.

        This uses the fact that Blender will ignore any command line arguments provided after the `--` command. This
        effectively extracts any arguments following `--`, and forwards them to the default `argparse.parse_args()`
        implementation.

        Args:
            None

        Returns:
            List[str]: The command line arguments provided to the Blender executable, and intended for the Python script.
        """
        try:
            double_dash_index = sys.argv.index("--")
            return sys.argv[double_dash_index + 1:]
        except ValueError:  # Case where no arguments were provided after `--`.
            return []

    def parse_args(self) -> argparse.Namespace:
        return super().parse_args(args=self._get_arguments_after_double_dash())


def main() -> None:
    """Decimation script for Blender."""

    # Parse the arguments provided to the script:
    parser = BlenderArgumentParser()
    parser.add_argument("--source", required=True, help="Path of the source file to decimate.")
    parser.add_argument("--destination", required=True, help="Path of the destination file to save.")
    parser.add_argument("--ratio", type=float, default=0.5, help="Mesh decimation ratio (between 0.0 and 1.0).")
    args = parser.parse_args()

    # Clear the Blender scene, effectively removing the default Cube, Light and Camera:
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the given OBJ file into the scene:
    bpy.ops.import_scene.obj(filepath=args.source)

    # Decimate the meshes of the scene using the provided decimation ratio.
    #
    # The decimation ratio represented the ratio of faces to keep from the original mesh:
    #   * At 1.0, the mesh remains unchanged.
    #   * At 0.5, edges have been collapsed in such a way that half the number of faces are retained.
    #   * At 0.0, all faces have been removed.
    for object in bpy.data.objects:
        if object.type == "MESH":
            modifier = object.modifiers.new(name="DecimateModifier", type="DECIMATE")
            modifier.ratio = args.ratio

    # Export the scene to the given USD file:
    bpy.ops.wm.usd_export(filepath=args.destination)


if __name__ == "__main__":
    main()
```

### Testing Our Mesh Decimation Script

Following best practices, this task can be executed locally from the command line. This makes it possible to develop, validate and debug it to allow fast iteration cycles, and also promotes reusability of components.

Before integrating our task, let's first make sure it runs as expected in standalone mode by running it from the command line:

``` shell
./blender \
    --background \
    --python path/to/job.blender-decimate.py \
    -- \
    --source path/to/source.obj \
    --destination path/to/destination.usd \
    --ratio 0.5
```

Using the mandatory Suzanne monkey as an OBJ source file, we should see the following result, with the original model on the left and its simplified version on the right:

<figure>
<p><img src="/images/ext_omniverse-farm_decimation-comparison.png" /></p>
<figcaption><p>Mesh decimation comparison</p></figcaption>
</figure>

### Integrating the Job with Farm Agent and Queue

Now that we know that our task works as expected, we will integrate it in Farm Agent so anyone can submit tasks and benefit from our work.

This can be done either by code, or by using a more User-friendly wizard that will assist in the creation of a task. Since we have already done a fair share of code for the day, let's use the wizard to make the rest of the day easier:

1.  Start the Farm Agent.

2.  Create a `blender-decimate` job definition (see `job.blender-decimate.kit` below) and upload it to the Queue.

The job definition contains the following details:

- Job name: `blender-decimate`.

- Job type: `Command or executable`, as we will be launching the `blender` executable. For other use cases, we could also select `Kit-based application` or `Kit-based service` to select a Kit extension as a driver for the process.

- Command: `blender${exe_ext}`, for which we can supply either the full path to Blender's executable on the Agent, or the name of any command to execute.

- Process arguments: The list of arguments to supply to the Blender command, one per line. These are the values common to all executions of this job.

- Allowed arguments: The parameters to supply to the job, which might differ from one execution to another. This can include a definition for `default` values, in case one is not supplied.

Let's now complete our project by submitting a task:

``` shell
curl -X POST "http://localhost:8222/queue/management/tasks/submit" \
    --header "Accept: application/json" \
    --header "Content-Type: application/json" \
    --data '{
    "user": "my-user-id",
    "task_type": "blender-decimate",
    "task_args": {
        "source": "path/to/suzanne.obj",
        "destination": "path/to/suzanne-decimated.usd",
        "ratio": 0.2
    },
    "task_comment": "My first decimation job!"
}
```

Note: Please wait a few seconds for an Agent to pick up the task.

Since jobs are defined in Kit files using the TOML syntax, the wizard will produce a schema similar to the code shown below, which agents use to launch and process our task. If you want to share or distribute your job to multiple machines, all you would have left to do would be to place it in the same location on other Agents of your pool.

> ``` toml
> # File: job.blender-decimate.kit
>
> [package]
> title = "Blender decimation task"
> description = "Decimate a mesh using Blender and export it as a USD asset"
> version = "1.0.0"
> category = "jobs"
> authors = ["Omniverse Team"]
> readme = "Omniverse decimation task"
> keywords = ["job"]
>
> # Schema for the Blender mesh decimation task.
> [job.blender-decimate]
> job_type = "base"
> name = "blender-decimate"
> log_to_stdout = true # Capture information from `stdout` and `stderr` for the task's logs
> # Since the `command` property supports standard Kit token resolution, we're using `${exe_ext}` so the executable resolves to `blender.exe` on Windows and
> # `blender` on Linux. For the environment where Agent will be running, we have the choice of either:
> #   * Making sure the `blender` executable can be found in the `PATH` or `HOME` environment variable.
> #   * Providing the full path to the Blender executable.
> command = "blender${exe_ext}"
> # The command line arguments listed in the `args` array will be supplied to the `command` for each task of this type. This has 2 main benefits:
> #    1. It prevents having to provide these arguments for each task.
> #    2. Makes it possible to seamlessly roll out updates to the "job.blender-decimate.py" script on the Agent, without the need for clients to also
> #       update their APIs. For example, Agents could update to a "job.blender-decimate.v2.py" and clients could still submit tasks using the same
> #       `allowed_args` listed below.
> args = [
>     "--background",
>     "--python", "path/to/job.blender-decimate.py",
>     "--", # In the case of Blender, this additional `--` token is required to supply arguments to the Python script itself.
> ]
>
> # The `allowed_args` are appended to the "static" `args` listed above for each task. Effectively, this means that the resulting command line executed by
> # Agents takes the form of:
> #    $ <command> <args> <allowed_args>
> #
> # In the case of our example, this resolves to:
> #    $ blender \
> #       --background --python path/to/job.blender-decimate.py -- \
> #       --source <source_obj> --destination <destination_usd> --ratio <ratio=0.5>
> #
> # Each `allowed_args` supports 2 properties:
> #    * `arg`: The argument token as it will appear on the command line.
> #    * `default`: A default value for the argument, if none is supplied by clients.
> #
> # Note that `allowed_args` defines the explicit list of arguments which can be submitted by clients, and that any additional arbitrary arguments will be
> # ignored. For security reasons, you would not want external clients to be able to supply extra arguments, which could otherwise allow arbitrary external
> # code execution. In our example, this prevents Users from submitting tasks to Blender with the `--python-expr <script>` argument, which executes the
> # provided text string as a Python script.
> [job.blender-decimate.allowed_args]
> source      = { arg = "--source",      default = "" }
> destination = { arg = "--destination", default = "" }
> ratio       = { arg = "--ratio",       default = "0.5" }
> ```

### Next Steps

To make this feature accessible to others, we can now bring it to the next level by:

- Writing a script or plugin to submit tasks directly from DCC applications making it possible for artists to submit tasks easily on asset revision.

- Alternatively, we could also submit tasks directly from our production tracking tools delivering automatic system submissions of tasks once they have been reviewed and approved.

Note: You may have noticed that it might be more performant for Agents to execute multiple tasks at the same time. Since an Agent is already launched, it might be more efficient to have it process a number of conversions at the same time, rather than only process a single file.

A few considerations:

- Perhaps we could edit our script to support supplying the path to a source **folder** to find and process all OBJ files, instead of a single file.

- Perhaps we could even provide our script with a [glob](https://docs.python.org/3/library/glob.html) wildcard pattern to find source files of multiple formats, and export them all as USD.

## Conclusion

With this ability to scale, distribute, and share tasks across multiple environments, there are no limits to what we could do automatically or by manual submission:

- Render turntable-style preview of assets once they are submitted to the production tracking system.

- Making sure all resources are checked in, and that no texture files are missing from files before .

- Validating that asset nomenclature conforms to studio requirements.

- Updating fluids or animation caches.

- Training machine learning on new datasets.

- and more...

Join the [Omniverse community](https://developer.nvidia.com/omniverse/community) to showcase your creations, or see what others have created.

### Kit-based Application Example

``` toml
# File: sample.job.kit-based.kit
# Description: Kit file containing the schema of a custom task type.

[package]
title = "Sample Kit Job"
description = "Sample Kit-based Job"
version = "0.1.0"
authors = ["You <your@email.com>"]
category = "jobs"
readme = "Omniverse Sample Kit-based Job"
repository = ""
keywords = ["job"]

[job.sample-kit-job]
name = "sample-kit-job"
job_type = "kit-service"
# Set the startup command for the job
command = "/opt/omniverse/composer/nv_internal.usd_composer.kit.sh"
args = [
    # Make sure Kit-based instances can be closed when the processing of the job has completed, and that the
    # notification asking if the USD stage from the active session should be saved prior to closing does not
    # prevent the application from shutting down:
    "--/app/file/ignoreUnsavedOnExit=true",
    # Make sure Kit-based instances are active upon launch, and that notification prompts asking for User
    # inputs are not preventing the session from being interactive:
    "--/app/extensions/excluded/0='omni.kit.window.privacy",
]
task_function = "sample-kit-job.run"
headless = true
env = {}
log_to_stdout = true

# Supply a list of folders where Extensions on which the job depends can be found:
[settings.app.exts.folders]
"++" = [
    "${job}/exts-job.sample.kit-based",
    # ...
]

# Provide the list of Extensions on which the job depends in order to execute scripts:
[dependencies]
"omni.services.farm.agent.runner" = {}
# ...

# When running a job, enable the following Extensions:
[settings.app.exts]
enabled = [
    # ...
]
```
