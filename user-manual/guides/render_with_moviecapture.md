# Rendering Using Movie Capture

Ensure that all Farm components are installed and running before continuing.

## Rendering with Farm

Composer comes bundled with the ability to submit render jobs to Queue.

In this example, we will walk through the needed steps to distribute your renders across your local network on spare machines. Follow the steps below to create a (render) task that an Agent will pick up and process. You can use or any other Omniverse Kit-based App with Movie Capture enabled.

### Requirements

- Farm Queue running locally or network accessible

- One or more Farm Agents

  - Running on systems with an NVIDIA GPU

  - Connected to the Farm Queue

  - With access to:

    - a properly configured `create-render` job definition.

    - the Kit application to launch for rendering.

    - all data required by the USD scenes being rendered.

The `create-render` job definition must be configured to use a Kit application accessible by Farm Agents. Any custom Kit applications, including those based on the Omniverse Kit Application Template, requires updating the `create-render` job definition. The `rendering_with_kit` guide explains how to do so.

### Send a Render to the Queue

It is important to ensure the scene you wish to render is stored in a location that is accessible to all Farm Agents, along with all the assets it contains.

1.  In Composer, open the scene you wish to render using `File` \> `Open`.

2.  Select `Rendering` \> `Movie Capture`.

<figure>
<p><img src="/images/ext_omniverse-farm_queue-submit-render.png" /></p>
<figcaption><p>Submitting a render to the Queue from <code>composer</code></p></figcaption>
</figure>

1.  In the `Queue Settings` section, ensure `Queue instance` is set to the host and port of your Farm Queue. The default for local installs is `localhost Queue`.

2.  `Optional`: Add a description to the task so you can easily identify it later. This can be useful for task recognition when running several tasks or for historical context of the jobs executed.

3.  Review and ensure all render settings and path locations are accurate.

4.  Ensure the `Output: Path` is set correctly.

5.  Submit the task to Queue by clicking `Submit to Queue` at the bottom of the `Movie Capture` panel.

Once submitted, the Queue dashboard will update and show the created task(s) with a status of `Submitted` while awaiting a suitable Agent to begin processing.

<figure>
<p><img src="/images/ext_omniverse-farm_queue-task_submitted.png" /></p>
<figcaption><p>Farm Task Dashboard</p></figcaption>
</figure>

### Add Agents to Execute on the Render Task

Agents are responsible for executing on tasks in Farm. To render the task, you will need one or more agents.

#### Agent Requirements

- Access to any file locations (including network locations) referenced by Farm tasks.

- Network Access to the Farm Queue services.

- Farm Agent service(s) running.

- Access to a properly configured `create-render` job definition.

- Suitable hardware.

To get started, ensure that there are one or more Farm Agents running.

1.  The default configuration assumes the Queue and Agent are both operating on `localhost`. If you are not running Agent on the same machine as Queue, modify the Farm configuration queue address and confirm the Agent is able to reach the Queue.

You can confirm which Agents are connected to the Farm Queue by going to the "Agents" tab of the Farm Dashboard.

<figure>
<p><img src="/images/ext_omniverse-farm_queue-agents.png" /></p>
<figcaption><p>Farm Queue Dashboard, Agent tab</p></figcaption>
</figure>

1.  Once connected, the Agent retrieves any suitable pending tasks from the Queue and will begin processing.

2.  The `Tasks` section of the Queue Dashboard will refresh after a few seconds and should reflect the new state of the system, where:

- The submitted task has transitioned to `Running`, which means processing is underway.

- The ID of the active task matches the one submitted earlier.

<figure>
<p><img src="/images/ext_omniverse-farm_queue-task_running.png" /></p>
<figcaption><p>Farm Queue Dashboard, Tasks tab</p></figcaption>
</figure>

Once the task has completed:

- Agent will return to `Idle` state.

- Task status will change to `Finished`.

In the Movie Capture panel, you can use the "folder-open" icon next to the `Output: Path` field, to open the output path and view the render results.
