// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { render, RenderResult } from "vitest-browser-react";
import { DagGraph } from "./dag-graph";
import { GraphEdge } from "~/utilities/graph-utility";
import { Task, TaskStatus } from "~/library/task-service";
import { useGraphData } from "~/hooks/graph-data";

function makeTask(partial: Partial<Task>): Task {
    return {
        // required
        id: partial.id ?? "",
        status: partial.status ?? "submitted",
        userId: partial.userId ?? "",
        type: partial.type ?? "",
        details: partial.details ?? "",
        args: partial.args ?? {},
        functionName: partial.functionName ?? "",
        functionArgs: partial.functionArgs ?? {},
        requirements: partial.requirements ?? {},
        comment: partial.comment ?? "",
        metrics: partial.metrics ?? null,
        progress: partial.progress ?? null,
        submissionS: partial.submissionS ?? 0,
        priority: partial.priority ?? 0,
        metadata:
            partial.metadata ??
            ({ dag: { id: "", name: "" } } as Task["metadata"]),
        submissionDate: partial.submissionDate ?? new Date(0),
        submissionDateString: partial.submissionDateString ?? "",
        labels: partial.labels ?? [],
        // allow overrides from partial last
        ...partial,
    } as Task;
}

const taskData: Task[] = [
    makeTask({
        id: "1",
        status: "finished",
        metadata: { dag: { id: "1", name: "Task 1" } },
    }),
    makeTask({
        id: "2",
        status: "running",
        metadata: { dag: { id: "2", name: "Task 2" } },
    }),
    makeTask({
        id: "3",
        status: "unscheduled",
        metadata: { dag: { id: "3", name: "Task 3" } },
    }),
];
const edges = [
    { source: "1", target: "2" },
    { source: "2", target: "3" },
];

// test helpers can be added here later as needed

function TestDagGraph({
    dagEdges,
    tasks,
}: {
    dagEdges: GraphEdge[];
    tasks: Task[];
}) {
    const { nodes, edges } = useGraphData({
        dagEdges,
        tasks,
        orientation: "horizontal",
    });
    return (
        <div style={{ width: 1200, height: 800 }}>
            <DagGraph nodes={nodes} edges={edges} />
        </div>
    );
}

const expectations = {
    expectGraphNodeVisible(
        screen: RenderResult,
        nodeTitle: string,
        status: TaskStatus
    ) {
        const cards = screen.baseElement.querySelectorAll("nve-card");
        const card = Array.from(cards).find(
            (card: Element) =>
                card.textContent?.includes(nodeTitle) &&
                card.textContent?.includes(status)
        );
        expect(card).toBeTruthy();
    },
    expectGraphNodeLengthToBe(screen: RenderResult, length: number) {
        const cards = screen.baseElement.querySelectorAll("nve-card");
        expect(cards.length).toBe(length);
    },
};

const actions = {
    renderGraph() {
        return render(<TestDagGraph dagEdges={edges} tasks={taskData} />);
    },
    rerenderGraph(
        screen: RenderResult,
        props: Parameters<typeof TestDagGraph>[0]
    ) {
        return screen.rerender(<TestDagGraph {...props} />);
    },
};

describe("table.tsx", () => {
    let screen: RenderResult;
    beforeEach(() => {
        screen = actions.renderGraph();
    });

    describe("graph", () => {
        it("should render the graph", () => {
            expectations.expectGraphNodeVisible(screen, "Task 1", "finished");
            expectations.expectGraphNodeVisible(screen, "Task 2", "running");
            expectations.expectGraphNodeVisible(
                screen,
                "Task 3",
                "unscheduled"
            );
            expectations.expectGraphNodeLengthToBe(screen, 3);
        });

        it("should render empty graph when no tasks are provided", () => {
            actions.rerenderGraph(screen, { dagEdges: edges, tasks: [] });
            expectations.expectGraphNodeLengthToBe(screen, 0);
        });

        it("should render disconnected graph when no edges are provided", () => {
            actions.rerenderGraph(screen, { dagEdges: [], tasks: taskData });
            expectations.expectGraphNodeLengthToBe(screen, 3);
        });
    });
});
