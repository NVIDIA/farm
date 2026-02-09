// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

const SECOND_IN_MS = 1000;
const MINUTE_IN_MS = 60 * SECOND_IN_MS;
const HOUR_IN_MS = 60 * MINUTE_IN_MS;
const DAY_IN_MS = 24 * HOUR_IN_MS;
const INFINITY_DATE_VALUE = 8640000000000000;
type DateParameters =
    | ConstructorParameters<DateConstructor>
    | [number, number, number, number?, number?, number?, number?];

const TimeUtility = {
    // Given a date object, returns a mm/dd/yyyy string.
    getMMDDYYYYinUTC(date: Date): string {
        // Use ISO UTC string.
        const [yyyy, mm, dd] = date.toISOString().split("T")[0].split("-");
        return `${mm}/${dd}/${yyyy}`;
    },
    // Given date constructor arguments, returns a copy of the date at the end of the local day.
    getEndOfDay(...args: DateParameters): Date {
        const clone = args.length === 1 ? new Date(args[0]) : new Date(...args);
        clone.setHours(23, 59, 59, 0);
        return clone;
    },
    // Given date constructor arguments, returns a copy of the date at the start of the local day.
    getStartOfDay(...args: DateParameters): Date {
        const clone = args.length === 1 ? new Date(args[0]) : new Date(...args);
        clone.setHours(0, 0, 0, 0);
        return clone;
    },
    getInfinityDate() {
        const date = new Date();
        date.setTime(INFINITY_DATE_VALUE);
        return date;
    },
    getNegativeInfinityDate() {
        const date = new Date();
        date.setTime(INFINITY_DATE_VALUE * -1);
        return date;
    },
    getLocalDateFromISODate(dateStr: string, endOfDay = false): Date {
        const [year, month, day] = dateStr
            .split("-")
            .map((num) => parseInt(num));
        const zeroIndexedMonth = month - 1;
        const date = new Date(year, zeroIndexedMonth, day);

        if (
            date.getFullYear() !== year ||
            date.getMonth() !== zeroIndexedMonth ||
            date.getDate() !== day
        ) {
            return new Date(NaN);
        }

        if (endOfDay) {
            date.setHours(23, 59, 59, 0);
        }

        return date;
    },
    // Given a mm/dd/yyyy string will return a timestamp in seconds. If shouldEndDay
    // is true, then the resulting timestamp will be the end of the day.
    getMMDDYYYYInSeconds(
        mmddyyyy: string,
        shouldEndDay = false
    ): number | undefined {
        if (!mmddyyyy) {
            return undefined;
        }

        const date = new Date(mmddyyyy);

        if (shouldEndDay) {
            date.setHours(23, 59, 59, 0);
        }

        return date.getTime() / 1000;
    },
    // Given a mm/dd/yyyy string, will return a timestamp in seconds for the beginning of
    // the supplied UTC day. If shouldEndDay is true, then the resulting timestamp will be
    // for the end of the day.
    getMMDDYYYYInSecondsUTC(
        mmddyyyy: string,
        shouldEndDay = false
    ): number | undefined {
        if (!mmddyyyy) {
            return undefined;
        }

        const [month, day, year] = mmddyyyy
            .split("/")
            .map((str) => parseInt(str));
        const hours = shouldEndDay ? 23 : 0;
        const minutes = shouldEndDay ? 59 : 0;
        const seconds = shouldEndDay ? 59 : 0;

        // Convert the mm/dd/yyyy UTC string to seconds since the epoch.
        return Date.UTC(year, month - 1, day, hours, minutes, seconds) / 1000;
    },
    // Given a date object, will return a string containing a human readable short
    // for timestamp including GMT timezone. E.g., Aug 10, 2022, 17:27:17 GMT.
    getCompactString(date: Date): string {
        const str = date.toUTCString();
        const [, day, month, year, time, timezone] = str.split(" ");
        return `${month} ${day}, ${year}, ${time} ${timezone}`;
    },
    getLocaleString(date: Date): string {
        return new Intl.DateTimeFormat(navigator.language, {
            year: "numeric",
            month: "short",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            timeZoneName: "shortGeneric",
            hour12: false,
        }).format(date);
    },
    // Given a date or timestamp, will determine how much time has elapsed since
    // that moment and return a human readable string with a rough estimate of
    // the elapsed time. E.g., 1 day ago, 2 hours ago, 15 minutes ago, or 10 seconds ago.
    getMajorTimeSinceString(date: Date | number): string {
        const historicMs =
            typeof date === "object" ? date.getMilliseconds() : date;
        const nowMs = Date.now();
        const differenceMs = nowMs - historicMs;

        const days = Math.floor(differenceMs / DAY_IN_MS);

        if (days > 0) {
            if (days === 1) {
                return `${days} day ago`;
            }
            return `${days} days ago`;
        }

        const remainingMsHours = differenceMs - days * DAY_IN_MS;

        const hours = Math.floor(remainingMsHours / HOUR_IN_MS);

        if (hours > 0) {
            if (hours === 1) {
                return `${hours} hour ago`;
            }
            return `${hours} hours ago`;
        }

        const remainingMsMinutes = remainingMsHours - hours * HOUR_IN_MS;

        const minutes = Math.floor(remainingMsMinutes / MINUTE_IN_MS);

        if (minutes > 0) {
            if (minutes === 1) {
                return `${minutes} minute ago`;
            }
            return `${minutes} minutes ago`;
        }

        const remainingMs = remainingMsMinutes - minutes * MINUTE_IN_MS;
        const seconds = Math.floor(remainingMs / SECOND_IN_MS);

        if (seconds === 1) {
            return `${seconds} second ago`;
        }

        return `${seconds} seconds ago`;
    },
    isValidDate(date: Date) {
        return !isNaN(date.getTime());
    },
} as const;

export { TimeUtility };
