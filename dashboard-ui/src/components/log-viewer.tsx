// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External
import Highlighter from "react-highlight-words";
import { useVirtualizer } from "@tanstack/react-virtual";
import type { JSX, Dispatch, SetStateAction } from "react";
import React, {
    useCallback,
    useLayoutEffect,
    useMemo,
    useRef,
    useState,
} from "react";
import { useDebouncedCallback } from "use-debounce";

// NVIDIA
import { Color } from "@nve/elements";
import type { IconName } from "@nve/elements";

// LOCAL
import { LogViewerWindowStyles } from "~/components/log-viewer.css";

export interface LogViewerProperties {
    logs: string;
}

type LogLevel = "error" | "warning" | "info";
type StateCount = Record<LogLevel, number>;
interface LogMeta {
    line: string;
    index: number;
    logLevel: LogLevel;
}
interface Filters {
    error: boolean;
    warning: boolean;
    info: boolean;
}

interface LogLineProps {
    line: string;
    lineNumber: number;
    searchText: string;
    focus: boolean;
    shouldWrap: boolean;
    logLevel: LogLevel;
    highlight: boolean;
    setFocusLine: Dispatch<SetStateAction<number>>;
}

interface FilterProps {
    counts: StateCount;
    filters: Filters;
    onFilterClicked: (filter: LogLevel) => void;
    onWrapChanged: () => void;
}

// Warning log line indicator.
const WARNING = "[warning]";
// Error log line indicator.
const ERROR = "[error]";

// Estimate of how many pixels used per character. Used for
// rough math.
const PIXEL_WIDTH_CHARACTER_ESTIMATE = 10;

// Gutter background color by log level.
const COLOR_MAP: Record<LogLevel, string> = {
    error: "#F03232",
    warning: "#F08039",
    info: "#3E64A3",
};

// Highlight color.
const HIGHLIGHT_COLOR = "yellowgreen";

// Helper function for creating a consistent set of useful data
// from a log line string.
function getLinesAsData(log: string): LogMeta[] {
    const lines = log.split("\n");

    return lines.map((line, index) => {
        const lowerLine = line.toLowerCase();

        return {
            line,
            index,
            logLevel:
                lowerLine.indexOf(ERROR) >= 0
                    ? "error"
                    : lowerLine.indexOf(WARNING) >= 0
                      ? "warning"
                      : "info",
        } as const;
    });
}

function Checkbox({
    label,
    onChange,
}: {
    label: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
    return (
        <nve-checkbox>
            <label>{label}</label>
            <input type="checkbox" onChange={onChange} />
        </nve-checkbox>
    );
}

function Textbox({
    onChange,
    placeholder,
}: {
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    placeholder?: string;
}) {
    return (
        <nve-input>
            <input type="text" onChange={onChange} placeholder={placeholder} />
        </nve-input>
    );
}

// Helper function for completely rendering an individual log line.
function LogLine({
    line,
    lineNumber,
    searchText,
    focus,
    shouldWrap,
    logLevel,
    highlight,
    setFocusLine,
}: LogLineProps) {
    const color = COLOR_MAP[logLevel];

    return (
        <div
            style={{
                overflowX: "visible",
                whiteSpace: shouldWrap ? "pre-wrap" : "pre",
                width: shouldWrap ? "" : "max-content",
                minWidth: shouldWrap ? "" : "100%",
                display: "grid",
                gridTemplateColumns: "50px 1fr",
            }}
            id={`LN${lineNumber}`}
        >
            <span
                role="button"
                tabIndex={0}
                onClick={() =>
                    setFocusLine((currentLine) => {
                        if (currentLine === lineNumber) {
                            return -1;
                        }
                        return lineNumber;
                    })
                }
                onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                        // Trigger onClick on Enter or Space key
                        setFocusLine((currentLine) => {
                            if (currentLine === lineNumber) {
                                return -1;
                            }
                            return lineNumber;
                        });
                    }
                }}
                style={{
                    display: "inline-block",
                    textAlign: "right",
                    color: "white",
                    backgroundColor: focus ? HIGHLIGHT_COLOR : color,
                    userSelect: "none",
                    paddingRight: 5,
                    height: "100%",
                }}
            >
                {lineNumber + 1}
            </span>
            <span
                style={{
                    paddingLeft: 5,
                }}
            >
                {highlight ? (
                    <Highlighter
                        highlightStyle={{ backgroundColor: HIGHLIGHT_COLOR }}
                        searchWords={searchText ? [searchText] : []}
                        autoEscape={true}
                        textToHighlight={line}
                    />
                ) : (
                    line
                )}
            </span>
        </div>
    );
}

function FilterRowButton({
    label,
    count,
    onClick,
    color,
    icon,
    active,
}: {
    onClick: () => void;
    count: number;
    label: string;
    color: Color;
    icon: IconName;
    active: boolean;
}) {
    return (
        <nve-badge
            style={{ cursor: "pointer" }}
            color={active ? color : "gray-slate"}
            onClick={() => onClick()}
        >
            <nve-icon name={icon} size="sm" />
            {`${count} ${label}${count > 1 ? "s" : ""}`}
        </nve-badge>
    );
}

// Helper function for rendering filters and counts.
function FiltersRow({
    counts,
    filters,
    onFilterClicked,
    onWrapChanged,
}: FilterProps): JSX.Element {
    return (
        <div nve-layout="row gap:sm align:vertical-center">
            <FilterRowButton
                color="blue-cobalt"
                count={counts.info}
                active={!!filters.info}
                icon="information-circle-stroke"
                label="info"
                onClick={() => onFilterClicked("info")}
            />
            <FilterRowButton
                color="red-cardinal"
                count={counts.error}
                active={!!filters.error}
                icon="stop-sign"
                label="error"
                onClick={() => onFilterClicked("error")}
            />
            <FilterRowButton
                color="orange-pumpkin"
                count={counts.warning}
                active={!!filters.warning}
                icon="traffic-cone"
                label="warning"
                onClick={() => onFilterClicked("warning")}
            />
            <Checkbox label="Wrap Lines" onChange={() => onWrapChanged()} />
        </div>
    );
}

// Primary render function for the LogViewer.
function LogViewer({ logs }: LogViewerProperties): JSX.Element {
    const [currentMatchIndex, setCurrentMatchIndex] = useState<number>(-1);
    const [searchText, setSearchText] = useState<string>("");
    const [filters, setFilters] = useState<Filters>({
        error: true,
        warning: true,
        info: true,
    });
    const [focusLine, setFocusLine] = useState<number>(-1);
    const [shouldWrap, setShouldWrap] = useState(false);
    const lines = useMemo(() => getLinesAsData(logs), [logs]);
    const { filteredLogLines, filteredLogCounts, filteredLogLineNumbers } =
        useMemo(() => {
            const logLines: LogMeta[] = [];
            const logCounts = { warning: 0, error: 0, info: 0 };
            const logLineNumbers = new Set<number>();
            for (const line of lines) {
                logCounts[line.logLevel] += 1;
                if (filters[line.logLevel]) {
                    logLines.push(line);
                    logLineNumbers.add(line.index);
                }
            }

            return {
                filteredLogLines: logLines,
                filteredLogCounts: logCounts,
                filteredLogLineNumbers: logLineNumbers,
            };
        }, [lines, filters]);

    const logLineIndexsMatchingSearchTerm = useMemo(() => {
        if (!searchText) {
            return [];
        }

        return lines.reduce((acc, { line, index }) => {
            if (
                filteredLogLineNumbers.has(index) &&
                line.includes(searchText)
            ) {
                acc.push(index);
            }

            return acc;
        }, [] as number[]);
    }, [lines, searchText, filteredLogLineNumbers]);

    const logLineIndexsMatchingSearchTermSet = useMemo(
        () => new Set(logLineIndexsMatchingSearchTerm),
        [logLineIndexsMatchingSearchTerm]
    );

    const estimateSizeCallback = useCallback(
        (index: number) => {
            if (!shouldWrap) return 16; // Default height per line

            const line = filteredLogLines[index].line ?? "";
            const containerWidth =
                parentRef.current?.clientWidth ?? window.innerWidth;

            const estimatedLines = Math.ceil(
                (line.length * PIXEL_WIDTH_CHARACTER_ESTIMATE) / containerWidth
            );

            return estimatedLines * 16; // Adjust height dynamically
        },
        [shouldWrap, filteredLogLines]
    );

    const parentRef = useRef<HTMLDivElement>(null);
    const rowVirtualizer = useVirtualizer({
        count: filteredLogLines.length,
        getScrollElement: () => parentRef.current,
        estimateSize: estimateSizeCallback,
    });

    useLayoutEffect(() => {
        function resizeLogViewer() {
            // We need to set the height of the log viewer so that react-virtual can properly lazily load elements, we want it to fill all remaining
            // space on the page to allow it to scroll
            if (parentRef.current) {
                const paddingOfContainer = 60;
                const height =
                    window.innerHeight -
                    parentRef.current.getBoundingClientRect().top -
                    paddingOfContainer;
                parentRef.current.style.height = `${height}px`;
            }

            rowVirtualizer.measure();
        }
        resizeLogViewer();

        window.addEventListener("resize", resizeLogViewer);
        return () => window.removeEventListener("resize", resizeLogViewer);
    }, [rowVirtualizer]);

    // Handler for when search input changes.
    const onSearchChange = useDebouncedCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const searchTerm = e.target.value;
            setSearchText(searchTerm);
            setFocusLine(-1);
            setCurrentMatchIndex(-1);
        },
        300
    );

    // Handler for setting state of filters on change.
    const onFilterClicked = useCallback(
        (filter: LogLevel) => {
            setFilters((currentFilters) => ({
                ...currentFilters,
                [filter]: !currentFilters[filter],
            }));
        },
        [setFilters]
    );

    // Handler for setting wrap state on change.
    const onWrapChanged = useCallback(() => {
        setShouldWrap((prevState) => !prevState);
        rowVirtualizer.measure();
    }, [rowVirtualizer]);

    // Handler for moving search back to the log origin.
    const onSearchUp = useCallback(() => {
        const newIndex =
            currentMatchIndex <= 0
                ? logLineIndexsMatchingSearchTerm.length - 1
                : currentMatchIndex - 1;
        const newLine = logLineIndexsMatchingSearchTerm[newIndex];
        const logLineIndex = filteredLogLines.findIndex(
            (logLine) => logLine.index === newLine
        );
        setCurrentMatchIndex(newIndex);
        rowVirtualizer.scrollToIndex(logLineIndex, { align: "center" });
        setFocusLine(newLine);
    }, [
        logLineIndexsMatchingSearchTerm,
        currentMatchIndex,
        rowVirtualizer,
        filteredLogLines,
    ]);

    // Handler for progressing search down the log.
    const onSearchDown = useCallback(() => {
        const newIndex =
            currentMatchIndex >= logLineIndexsMatchingSearchTerm.length - 1
                ? 0
                : currentMatchIndex + 1;
        const newLine = logLineIndexsMatchingSearchTerm[newIndex];
        const logLineIndex = filteredLogLines.findIndex(
            (logLine) => logLine.index === newLine
        );
        setCurrentMatchIndex(newIndex);
        rowVirtualizer.scrollToIndex(logLineIndex, { align: "center" });
        setFocusLine(newLine);
    }, [
        logLineIndexsMatchingSearchTerm,
        currentMatchIndex,
        rowVirtualizer,
        filteredLogLines,
    ]);

    return (
        <div nve-layout="column gap:md align:stretch">
            <FiltersRow
                counts={filteredLogCounts}
                filters={filters}
                onFilterClicked={onFilterClicked}
                onWrapChanged={onWrapChanged}
            />

            <div>
                <Textbox
                    placeholder="Enter search terms..."
                    onChange={onSearchChange}
                />
            </div>

            {logLineIndexsMatchingSearchTerm.length === 0 || !searchText ? (
                <div>
                    <nve-badge color="gray-slate" container="flat">
                        {!searchText ? "No active search" : "No matches found"}
                    </nve-badge>
                </div>
            ) : (
                <div>
                    <span>
                        <nve-badge color="gray-slate">
                            {currentMatchIndex + 1} /{" "}
                            {logLineIndexsMatchingSearchTerm.length}
                        </nve-badge>
                    </span>

                    <span style={{ marginLeft: "1em" }}>
                        <nve-badge
                            color={
                                currentMatchIndex > 0
                                    ? "brand-green"
                                    : "gray-slate"
                            }
                            onClick={() => onSearchUp()}
                        >
                            <nve-icon name="arrow" size="sm" direction="up" />
                        </nve-badge>
                    </span>

                    <span style={{ marginLeft: "0.5em" }}>
                        <nve-badge
                            color={
                                currentMatchIndex <
                                logLineIndexsMatchingSearchTerm.length - 1
                                    ? "brand-green"
                                    : "gray-slate"
                            }
                            onClick={() => onSearchDown()}
                        >
                            <nve-icon name="arrow" size="sm" direction="down" />
                        </nve-badge>
                    </span>
                </div>
            )}

            <div ref={parentRef} className={LogViewerWindowStyles}>
                <div
                    style={{
                        height: `${rowVirtualizer.getTotalSize()}px`,
                        width: "100%",
                        position: "relative",
                    }}
                >
                    {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                        const log = filteredLogLines[virtualRow.index];
                        const focus = focusLine === log.index;
                        return (
                            <div
                                key={virtualRow.index}
                                className={
                                    virtualRow.index % 2
                                        ? "ListItemOdd"
                                        : "ListItemEven"
                                }
                                style={{
                                    position: "absolute",
                                    top: 0,
                                    left: 0,
                                    minWidth: "100%",
                                    transform: `translateY(${virtualRow.start}px)`,
                                    outline: focus
                                        ? `2px solid ${HIGHLIGHT_COLOR}`
                                        : "",
                                    zIndex: focus ? 10 : 1,
                                    opacity: focusLine >= 0 && !focus ? 0.5 : 1,
                                }}
                            >
                                <LogLine
                                    line={log.line}
                                    lineNumber={log.index}
                                    searchText={searchText}
                                    shouldWrap={shouldWrap}
                                    logLevel={log.logLevel}
                                    focus={focus}
                                    setFocusLine={setFocusLine}
                                    highlight={logLineIndexsMatchingSearchTermSet.has(
                                        log.index
                                    )}
                                />
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}

export { LogViewer };
