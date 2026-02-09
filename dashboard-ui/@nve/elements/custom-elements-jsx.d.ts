// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * This type can be used to create scoped tags for your components.
 *
 * Usage:
 *
 * ```ts
 * import type { ScopedElements } from "path/to/library/jsx-integration";
 *
 * declare module "my-library" {
 *   namespace JSX {
 *     interface IntrinsicElements
 *       extends ScopedElements<'test-', ''> {}
 *   }
 * }
 * ```
 *
 */
export type ScopedElements<Prefix extends string = "", Suffix extends string = ""> = {
  [Key in keyof CustomElements as `${Prefix}${Key}${Suffix}`]: CustomElements[Key];
};

type BaseProps = {
  /** Content added between the opening and closing tags of the element */
  children?: any;
  /** Used for declaratively styling one or more elements using CSS (Cascading Stylesheets) */
  class?: string;
  /** Used for declaratively styling one or more elements using CSS (Cascading Stylesheets) */
  className?: string;
  /** Takes an object where the key is the class name(s) and the value is a boolean expression. When true, the class is applied, and when false, it is removed. */
  classList?: Record<string, boolean | undefined>;
  /** Specifies the text direction of the element. */
  dir?: "ltr" | "rtl";
  /** Contains a space-separated list of the part names of the element that should be exposed on the host element. */
  exportparts?: string;
  /** For <label> and <output>, lets you associate the label with some control. */
  htmlFor?: string;
  /** Specifies whether the element should be hidden. */
  hidden?: boolean | string;
  /** A unique identifier for the element. */
  id?: string;
  /** Keys tell React which array item each component corresponds to */
  key?: string | number;
  /** Specifies the language of the element. */
  lang?: string;
  /** Contains a space-separated list of the part names of the element. Part names allows CSS to select and style specific elements in a shadow tree via the ::part pseudo-element. */
  part?: string;
  /** Use the ref attribute with a variable to assign a DOM element to the variable once the element is rendered. */
  ref?: unknown | ((e: unknown) => void);
  /** Adds a reference for a custom element slot */
  slot?: string;
  /** Prop for setting inline styles */
  style?: Record<string, string | number>;
  /** Overrides the default Tab button behavior. Avoid using values other than -1 and 0. */
  tabIndex?: number;
  /** Specifies the tooltip text for the element. */
  title?: string;
  /** Passing 'no' excludes the element content from being translated. */
  translate?: "yes" | "no";
};

type BaseEvents = {
  onClick?: (event: MouseEvent) => void;
  onKeyDown?: (event: KeyboardEvent) => void;
  onKeyUp?: (event: KeyboardEvent) => void;
  onKeyPressed?: (event: KeyboardEvent) => void;
  onFocus?: (event: FocusEvent) => void;
  onBlur?: (event: FocusEvent) => void;
  onMouseEnter?: (event: MouseEvent) => void;
  onMouseLeave?: (event: FocusEvent) => void;
  onMouseMove?: (event: FocusEvent) => void;
  onPointerDown?: (event: PointerEvent) => void;
  onPointerUp?: (event: PointerEvent) => void;
  onPointerMove?: (event: PointerEvent) => void;
};

export type AccordionHeaderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /**  */
  slot?: string;
};

export type AccordionContentProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type AccordionProps = {
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container.
- `undefined` Element container is optimized for embedding or being inset inside another containing element. */
  container?: "flat" | "inset" | "default";
  /** Indicates whether collapsible content is currently visible or hidden from the user. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-expanded)
- `undefined` The associated content is expanded and visible to the user.
- `undefined` The associated content is collapsed and hidden from the user. */
  expanded?: boolean;
  /** This Boolean attribute prevents the user from interacting with the element: it cannot be pressed or focused. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-disabled)
- `undefined` The element is disabled and cannot be interacted with.
- `undefined` The element is enabled and can be interacted with. */
  disabled?: boolean;
  /** Determines whether or not the accordion should opt-in to stateful expansion behavior (defaults to stateless) */
  "behavior-expand"?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type AccordionGroupProps = {
  /** Determines whether or not the accordion should opt-in to stateful expansion behavior (defaults to stateless) */
  "behavior-expand"?: boolean;
  /** Determines whether or not the accordion should opt-in to stateful expansion of a single accordion at a time */
  "behavior-expand-single"?: boolean;
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container.
- `undefined` Element container is optimized for embedding or being inset inside another containing element. */
  container?: "flat" | "inset" | "default";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type AlertBannerProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Highlights important actions or draws attention to primary interactive elements.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation. */
  status?: "accent" | "warning" | "success" | "danger" | "default";
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Increases visual weight to draw attention and highlight important elements. */
  prominence?: "emphasis" | "default";
  /** Defines a base color from the theme color palette */
  color?:
    | "red-cardinal"
    | "gray-slate"
    | "gray-denim"
    | "blue-indigo"
    | "blue-cobalt"
    | "blue-sky"
    | "teal-cyan"
    | "green-mint"
    | "teal-seafoam"
    | "green-grass"
    | "yellow-amber"
    | "orange-pumpkin"
    | "red-tomato"
    | "pink-magenta"
    | "purple-plum"
    | "purple-violet"
    | "purple-lavender"
    | "pink-rose"
    | "green-jade"
    | "lime-pear"
    | "yellow-nova"
    | "brand-green";
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element container is optimized for filling its container bounds. */
  container?: "full" | "default";
};

export type AlertGroupProps = {
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Highlights important actions or draws attention to primary interactive elements.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation. */
  status?: "accent" | "warning" | "success" | "danger" | "default";
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Increases visual weight to draw attention and highlight important elements. */
  prominence?: "emphasis" | "default";
  /** Defines a base color from the theme color palette */
  color?:
    | "red-cardinal"
    | "gray-slate"
    | "gray-denim"
    | "blue-indigo"
    | "blue-cobalt"
    | "blue-sky"
    | "teal-cyan"
    | "green-mint"
    | "teal-seafoam"
    | "green-grass"
    | "yellow-amber"
    | "orange-pumpkin"
    | "red-tomato"
    | "pink-magenta"
    | "purple-plum"
    | "purple-violet"
    | "purple-lavender"
    | "pink-rose"
    | "green-jade"
    | "lime-pear"
    | "yellow-nova"
    | "brand-green";
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element container is optimized for filling its container bounds. */
  container?: "full" | "default";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type AlertProps = {
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive.
- `undefined` Highlights important actions or draws attention to primary interactive elements.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation.
- `undefined` Task has been scheduled for future execution at a specific time.
- `undefined` Task is waiting in line to begin after other tasks complete.
- `undefined` Task is awaiting approval, user input, or external conditions before proceeding.
- `undefined` Task is initializing and preparing to begin active execution.
- `undefined` Task is actively executing and making progress.
- `undefined` Task is being restarted after an interruption or reset.
- `undefined` Task is gracefully shutting down and completing cleanup operations.
- `undefined` Task has completed successfully with the expected outcome.
- `undefined` Task encountered an error and did not complete as intended.
- `undefined` Task status cannot be determined or is unavailable.
- `undefined` Task was intentionally skipped or excluded from execution. */
  status?:
    | "accent"
    | "warning"
    | "success"
    | "danger"
    | "scheduled"
    | "queued"
    | "pending"
    | "starting"
    | "running"
    | "restarting"
    | "stopping"
    | "finished"
    | "failed"
    | "unknown"
    | "ignored"
    | "muted"
    | "default";
  /** Indicates whether the element can be dismissed or closed by the user.
- `undefined` The element displays a close control and can be dismissed by the user.
- `undefined` The element cannot be closed by the user and requires programmatic dismissal. */
  closable?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";

  /** Dispatched when the alert is closed within a alert group. */
  onclose?: (e: CustomEvent<never>) => void;
};

export type AppHeaderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type AvatarGroupProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type AvatarProps = {
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts.
- `undefined` Extra small size for very small elements or very dense layouts. */
  size?: "sm" | "md" | "lg" | "xs" | "default";
  /** Defines a base color from the theme color palette */
  color?:
    | "red-cardinal"
    | "gray-slate"
    | "gray-denim"
    | "blue-indigo"
    | "blue-cobalt"
    | "blue-sky"
    | "teal-cyan"
    | "green-mint"
    | "teal-seafoam"
    | "green-grass"
    | "yellow-amber"
    | "orange-pumpkin"
    | "red-tomato"
    | "pink-magenta"
    | "purple-plum"
    | "purple-violet"
    | "purple-lavender"
    | "pink-rose"
    | "green-jade"
    | "lime-pear"
    | "yellow-nova"
    | "brand-green";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type BadgeProps = {
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Highlights important actions or draws attention to primary interactive elements.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation.
- `undefined` Task has been scheduled for future execution at a specific time.
- `undefined` Task is waiting in line to begin after other tasks complete.
- `undefined` Task is awaiting approval, user input, or external conditions before proceeding.
- `undefined` Task is initializing and preparing to begin active execution.
- `undefined` Task is actively executing and making progress.
- `undefined` Task is being restarted after an interruption or reset.
- `undefined` Task is gracefully shutting down and completing cleanup operations.
- `undefined` Task has completed successfully with the expected outcome.
- `undefined` Task encountered an error and did not complete as intended.
- `undefined` Task status cannot be determined or is unavailable.
- `undefined` Task was intentionally skipped or excluded from execution. */
  status?:
    | "scheduled"
    | "queued"
    | "pending"
    | "starting"
    | "running"
    | "restarting"
    | "stopping"
    | "finished"
    | "failed"
    | "unknown"
    | "ignored"
    | "accent"
    | "warning"
    | "success"
    | "danger";
  /** Defines a base color from the theme color palette */
  color?:
    | "red-cardinal"
    | "gray-slate"
    | "gray-denim"
    | "blue-indigo"
    | "blue-cobalt"
    | "blue-sky"
    | "teal-cyan"
    | "green-mint"
    | "teal-seafoam"
    | "green-grass"
    | "yellow-amber"
    | "orange-pumpkin"
    | "red-tomato"
    | "pink-magenta"
    | "purple-plum"
    | "purple-violet"
    | "purple-lavender"
    | "pink-rose"
    | "green-jade"
    | "lime-pear"
    | "yellow-nova"
    | "brand-green";
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container. */
  container?: "flat" | "default";
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Increases visual weight to draw attention and highlight important elements. */
  prominence?: "emphasis" | "default";
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type BreadcrumbProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type ButtonGroupProps = {
  /** By default the button group is stateless. Add the `behavior-select` attribute and set to `single` or `multi` to enable stateful selction handling. */
  "behavior-select"?: "single" | "multi";
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container. */
  container?: "flat" | "rounded" | "default";
  /** Controls the directional flow of the element's layout and interaction pattern.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content in a vertical stack with block-level spacing. */
  orientation?: "horizontal" | "vertical" | "default";
  /** The Interaction type provides a way to indicate the intent of an interactive element. This can help users quickly understand what each interaction will do and reduce the potential for confusion or errors.
- `undefined` Increases visual weight to draw attention and highlight important elements.
- `undefined` Indicates the interaction is intended to be used for destructive actions such as deleting or removing. */
  interaction?: "emphasis" | "destructive";
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts. */
  size?: "sm" | "md" | "lg" | "default";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type ButtonProps = {
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container.
- `undefined` Element container is reduced to fit within inline content such as a block of text. */
  container?: "flat" | "inline" | "default";
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts. */
  size?: "sm" | "md" | "lg" | "default";
  /** The Interaction type provides a way to indicate the intent of an interactive element. This can help users quickly understand what each interaction will do and reduce the potential for confusion or errors.
- `undefined` Increases visual weight to draw attention and highlight important elements.
- `undefined` Indicates the interaction is intended to be used for destructive actions such as deleting or removing. */
  interaction?: "emphasis" | "destructive";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Indicates the current state of a toggle button that can be switched on or off. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-pressed)
- `undefined` The button is in the pressed (on) state and the associated action or setting is active.
- `undefined` The button is in the unpressed (off) state and the associated action or setting is inactive. */
  pressed?: boolean;
  /** Indicates whether collapsible content is currently visible or hidden from the user. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-expanded)
- `undefined` The associated content is expanded and visible to the user.
- `undefined` The associated content is collapsed and hidden from the user. */
  expanded?: boolean;
  /** Indicates whether the element's value can be modified by the user while remaining visible and focusable. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/readonly)
- `undefined` The element is readonly and its value cannot be changed, but can still be focused and copied.
- `undefined` The element is editable and the user can modify its value through interaction. */
  readonly?: boolean;
  /** Similar to input form, sets a button to submit a form outside its parent form.
Returns a reference to the form element if available.
https://developer.mozilla.org/en-US/docs/Web/API/ElementInternals/form */
  form?: HTMLFormElement | null | string;
  /** The name of the element, submitted as a pair with the element value as part of the form data. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-name) */
  name?: string;
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: string;
  /** Defines the button behavior when associated within an <form> element.
https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-type */
  type?: "button" | "submit" | "reset";
  /** This Boolean attribute prevents the user from interacting with the element: it cannot be pressed or focused. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-disabled)
- `undefined` The element is disabled and cannot be interacted with.
- `undefined` The element is enabled and can be interacted with. */
  disabled?: boolean;
  /** Indicates whether an element is currently chosen within a multi-option selection group. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-selected)
- `undefined` The element is selected and represents the user's current choice within the group.
- `undefined` The element is not selected and is available to be chosen by the user. */
  selected?: boolean;
  /** Indicates the element that represents the user's current location or position within a set. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-current)
- `page` - Marks the current page within a set of navigation links.
- `step` - Marks the current step within a multi-step process or workflow. */
  current?: "page" | "step";
  /** Establishing a relationship between a popover and its invoker button.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetElement */
  popoverTargetElement?: HTMLElement;
  /** The id of the element to which the popover is applied.
https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button#popovertarget */
  popovertarget?: string;
  /** The popover target action to be applied to the popover target element.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetAction */
  popovertargetaction?: "show" | "hide" | "toggle";
  /** The id of the element to which the command is applied.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  commandfor?: string;
  /** The command to be applied to the element.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  command?: string;
};

export type CardProps = {
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container.
- `undefined` Element container is optimized for filling its container bounds. */
  container?: "flat" | "full" | "default";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type CardHeaderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /**  */
  slot?: string;
};

export type CardContentProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type CardFooterProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /**  */
  slot?: string;
};

export type ChatMessageProps = {
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container. */
  container?: "flat";
  /** Defines a base color from the theme color palette */
  color?:
    | "red-cardinal"
    | "gray-slate"
    | "gray-denim"
    | "blue-indigo"
    | "blue-cobalt"
    | "blue-sky"
    | "teal-cyan"
    | "green-mint"
    | "teal-seafoam"
    | "green-grass"
    | "yellow-amber"
    | "orange-pumpkin"
    | "red-tomato"
    | "pink-magenta"
    | "purple-plum"
    | "purple-violet"
    | "purple-lavender"
    | "pink-rose"
    | "green-jade"
    | "lime-pear"
    | "yellow-nova"
    | "brand-green";
  /**  */
  "arrow-position"?: "top-start" | "top-end" | "bottom-start" | "bottom-end";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type CheckboxGroupProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";
};

export type CheckboxProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type ColorProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type ComboboxProps = {
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container. */
  container?: "flat";
  /** Disable rendering of inline tags for multiple select */
  notags?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type CopyButtonProps = {
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Determines if the copy button should auto write to clipboard by the trigger. */
  "behavior-copy"?: boolean;
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container.
- `undefined` Element container is reduced to fit within inline content such as a block of text. */
  container?: "flat" | "inline" | "default";
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts. */
  size?: "sm" | "md" | "lg" | "default";
  /** The Interaction type provides a way to indicate the intent of an interactive element. This can help users quickly understand what each interaction will do and reduce the potential for confusion or errors.
- `undefined` Increases visual weight to draw attention and highlight important elements.
- `undefined` Indicates the interaction is intended to be used for destructive actions such as deleting or removing. */
  interaction?: "emphasis" | "destructive";
  /** Indicates the current state of a toggle button that can be switched on or off. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-pressed)
- `undefined` The button is in the pressed (on) state and the associated action or setting is active.
- `undefined` The button is in the unpressed (off) state and the associated action or setting is inactive. */
  pressed?: boolean;
  /** Indicates whether collapsible content is currently visible or hidden from the user. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-expanded)
- `undefined` The associated content is expanded and visible to the user.
- `undefined` The associated content is collapsed and hidden from the user. */
  expanded?: boolean;
  /** Indicates whether the element's value can be modified by the user while remaining visible and focusable. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/readonly)
- `undefined` The element is readonly and its value cannot be changed, but can still be focused and copied.
- `undefined` The element is editable and the user can modify its value through interaction. */
  readonly?: boolean;
  /** Similar to input form, sets a button to submit a form outside its parent form.
Returns a reference to the form element if available.
https://developer.mozilla.org/en-US/docs/Web/API/ElementInternals/form */
  form?: HTMLFormElement | null | string;
  /** The name of the element, submitted as a pair with the element value as part of the form data. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-name) */
  name?: string;
  /** Defines the button behavior when associated within an <form> element.
https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-type */
  type?: "button" | "submit" | "reset";
  /** This Boolean attribute prevents the user from interacting with the element: it cannot be pressed or focused. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-disabled)
- `undefined` The element is disabled and cannot be interacted with.
- `undefined` The element is enabled and can be interacted with. */
  disabled?: boolean;
  /** Indicates whether an element is currently chosen within a multi-option selection group. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-selected)
- `undefined` The element is selected and represents the user's current choice within the group.
- `undefined` The element is not selected and is available to be chosen by the user. */
  selected?: boolean;
  /** Indicates the element that represents the user's current location or position within a set. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-current)
- `page` - Marks the current page within a set of navigation links.
- `step` - Marks the current step within a multi-step process or workflow. */
  current?: "page" | "step";
  /** Establishing a relationship between a popover and its invoker button.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetElement */
  popoverTargetElement?: HTMLElement;
  /** The id of the element to which the popover is applied.
https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button#popovertarget */
  popovertarget?: string;
  /** The popover target action to be applied to the popover target element.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetAction */
  popovertargetaction?: "show" | "hide" | "toggle";
  /** The id of the element to which the command is applied.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  commandfor?: string;
  /** The command to be applied to the element.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  command?: string;
};

export type DateProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type DatetimeProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type DialogFooterProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type DialogHeaderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type DialogProps = {
  /** Determines the position of an element along both inline and block axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Box_alignment_in_grid_layout#the_two_axes_of_a_grid_layout)
- `undefined` Centers the popover along the anchor's edge for balanced positioning.
- `undefined` Positions the popover above the anchor element.
- `undefined` Positions the popover below the anchor element.
- `undefined` Positions the popover to the left side of the anchor element.
- `undefined` Positions the popover to the right side of the anchor element. */
  position?: "center" | "top" | "bottom" | "left" | "right";
  /** Determines the alignment of the popover relative to the provided anchor element.
- `undefined` Aligns the popover to the beginning edge of the anchor for left or top alignment.
- `undefined` Aligns the popover to the ending edge of the anchor for right or bottom alignment.
- `undefined` Centers the popover along the anchor's edge for balanced positioning. */
  alignment?: "start" | "end" | "center";
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts. */
  size?: "sm" | "md" | "lg" | "default";
  /** Indicates whether the element can be dismissed or closed by the user.
- `undefined` The element displays a close control and can be dismissed by the user.
- `undefined` The element cannot be closed by the user and requires programmatic dismissal. */
  closable?: boolean;
  /** Determines if a dialog should have a modal backdrop that visually overlays the UI. */
  modal?: boolean;
  /** Provides the element that the popover should position relative to. Anchor can accept a idref string within the same render root or a HTMLElement DOM reference. */
  anchor?: string | HTMLElement;
  /** Defines what element triggers an `open` interaction event. A trigger can accept a idref string within the same render root or a HTMLElement DOM reference. */
  trigger?: string | HTMLElement;
  /** Determines if popover visibility behavior should be automatically controlled by the trigger. */
  "behavior-trigger"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";

  /** Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event) */
  onbeforetoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event) */
  ontoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched when the dialog is opened. */
  onopen?: (e: CustomEvent<never>) => void;
  /** Dispatched when the dialog is closed. */
  onclose?: (e: CustomEvent<never>) => void;
};

export type DividerProps = {
  /** Controls the directional flow of the element's layout and interaction pattern.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content in a horizontal row with block-level spacing. */
  orientation?: "vertical" | "horizontal";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type DotProps = {
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Highlights important actions or draws attention to primary interactive elements.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation.
- `undefined` Task has been scheduled for future execution at a specific time.
- `undefined` Task is waiting in line to begin after other tasks complete.
- `undefined` Task is awaiting approval, user input, or external conditions before proceeding.
- `undefined` Task is initializing and preparing to begin active execution.
- `undefined` Task is actively executing and making progress.
- `undefined` Task is being restarted after an interruption or reset.
- `undefined` Task is gracefully shutting down and completing cleanup operations.
- `undefined` Task has completed successfully with the expected outcome.
- `undefined` Task encountered an error and did not complete as intended.
- `undefined` Task status cannot be determined or is unavailable.
- `undefined` Task was intentionally skipped or excluded from execution. */
  status?:
    | "accent"
    | "warning"
    | "success"
    | "danger"
    | "scheduled"
    | "queued"
    | "pending"
    | "starting"
    | "running"
    | "restarting"
    | "stopping"
    | "finished"
    | "failed"
    | "unknown"
    | "ignored";
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts. */
  size?: "sm" | "md" | "lg";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type DrawerContentProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type DrawerFooterProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type DrawerHeaderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type DrawerProps = {
  /** Determines the position of an element along both inline and block axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Box_alignment_in_grid_layout#the_two_axes_of_a_grid_layout)
- `undefined` Positions the popover to the left side of the anchor element.
- `undefined` Positions the popover to the right side of the anchor element.
- `undefined` Positions the popover below the anchor element.
- `undefined` Positions the popover above the anchor element. */
  position?: "left" | "right" | "bottom" | "top";
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts. */
  size?: "sm" | "md" | "lg" | "default";
  /** Indicates whether the element can be dismissed or closed by the user.
- `undefined` The element displays a close control and can be dismissed by the user.
- `undefined` The element cannot be closed by the user and requires programmatic dismissal. */
  closable?: boolean;
  /** Determines if a drawer should have a modal backdrop that visually overlays the UI. */
  modal?: boolean;
  /** Provides the element that the popover should position relative to. Anchor can accept a idref string within the same render root or a HTMLElement DOM reference. */
  anchor?: string | HTMLElement;
  /** Defines what element triggers an `open` interaction event. A trigger can accept a idref string within the same render root or a HTMLElement DOM reference. */
  trigger?: string | HTMLElement;
  /** Create a inline layout effect while retaining the a11y characteristics and top layer behavior (light dismiss, focus trap, non interactive background)
https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ */
  inline?: boolean;
  /** Determines if popover visibility behavior should be automatically controlled by the trigger. */
  "behavior-trigger"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";

  /** Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event) */
  onbeforetoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event) */
  ontoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched when the drawer is opened. */
  onopen?: (e: CustomEvent<never>) => void;
  /** Dispatched when the drawer is closed. */
  onclose?: (e: CustomEvent<never>) => void;
};

export type DropdownGroupProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";

  /** Dispatched when a dropdown in the group is opened */
  onopen?: (e: CustomEvent<never>) => void;
  /** Dispatched when a dropdown in the group is closed */
  onclose?: (e: CustomEvent<never>) => void;
};

export type DropdownFooterProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type DropdownHeaderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type DropdownProps = {
  /** Provides the element that the popover should position relative to. Anchor can accept a idref string within the same render root or a HTMLElement DOM reference. */
  anchor?: string | HTMLElement;
  /** Defines what element triggers an `open` interaction event. A trigger can accept a idref string within the same render root or a HTMLElement DOM reference. */
  trigger?: string | HTMLElement;
  /** Determines the position of an element along both inline and block axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Box_alignment_in_grid_layout#the_two_axes_of_a_grid_layout)
- `undefined` Centers the popover along the anchor's edge for balanced positioning.
- `undefined` Positions the popover above the anchor element.
- `undefined` Positions the popover below the anchor element.
- `undefined` Positions the popover to the left side of the anchor element.
- `undefined` Positions the popover to the right side of the anchor element. */
  position?: "center" | "top" | "bottom" | "left" | "right";
  /** Determines the alignment of the popover relative to the provided anchor element.
- `undefined` Aligns the popover to the beginning edge of the anchor for left or top alignment.
- `undefined` Aligns the popover to the ending edge of the anchor for right or bottom alignment.
- `undefined` Centers the popover along the anchor's edge for balanced positioning. */
  alignment?: "start" | "end" | "center";
  /** Determines if popover visibility behavior should be automatically controlled by the trigger. */
  "behavior-trigger"?: boolean;
  /** Indicates whether the element can be dismissed or closed by the user.
- `undefined` The element displays a close control and can be dismissed by the user.
- `undefined` The element cannot be closed by the user and requires programmatic dismissal. */
  closable?: boolean;
  /** Determines if an arrow should be rendered. */
  arrow?: boolean;
  /**  */
  modal?: boolean;
  /**  */
  "popover-type"?: "auto" | "manual" | "hint" | "inline";
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /**  */
  popoverArrow?: HTMLElement;
  /** Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event) */
  onbeforetoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event) */
  ontoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched when the dropdown is opened. */
  onopen?: (e: CustomEvent<never>) => void;
  /** Dispatched when the dropdown is closed. */
  onclose?: (e: CustomEvent<never>) => void;
};

export type DropzoneProps = {
  /**  */
  accept?: string;
  /**  */
  "max-file-size"?: number;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: array;
  /** emits when the value has changed (files located in event.target) */
  onchange?: (e: CustomEvent<never>) => void;
};

export type FileProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type ControlGroupProps = {
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type ControlMessageProps = {
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled" | "default";
  /** Validation error code for current form control
https://developer.mozilla.org/en-US/docs/Web/API/ValidityState */
  error?:
    | "badInput"
    | "customError"
    | "patternMismatch"
    | "rangeOverflow"
    | "rangeUnderflow"
    | "stepMismatch"
    | "tooLong"
    | "tooShort"
    | "typeMismatch"
    | "valid"
    | "valueMissing";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /**  */
  slot?: string;
};

export type ControlProps = {
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type GridCellProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type GridColumnProps = {
  /** Columns can individually have set widths using the `width` property or attribute and a valid CSS value type.
If the total width of all columns is less than the grid width then the last column will fill the remaining space.
By default columns are evenly devided unless width is explicitly provided. Content within a cell of a given
column will wrap content to fit the width of the column. */
  width?: string;
  /** Determines the position of an element along both inline and block axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Box_alignment_in_grid_layout#the_two_axes_of_a_grid_layout) */
  position?: "fixed" | "sticky" | "";
  /** Control the content alignment within a given column.
- `undefined` Aligns the popover to the beginning edge of the anchor for left or top alignment.
- `undefined` Centers the popover along the anchor's edge for balanced positioning.
- `undefined` Aligns the popover to the ending edge of the anchor for right or bottom alignment. */
  "column-align"?: "start" | "center" | "end";
  /**  */
  "aria-colindex"?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";

  /**  */
  "onnve-grid-column-resize"?: (e: CustomEvent<CustomEvent>) => void;
};

export type GridFooterProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /**  */
  slot?: string;
};

export type GridProps = {
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container.
- `undefined` Element container is optimized for filling its container bounds. */
  container?: "flat" | "full" | "default";
  /** Determine style variant stripe rows */
  stripe?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type GridHeaderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type GridPlaceholderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type GridRowProps = {
  /** Indicates whether an element is currently chosen within a multi-option selection group. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-selected)
- `undefined` The element is selected and represents the user's current choice within the group.
- `undefined` The element is not selected and is available to be chosen by the user. */
  selected?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type IconButtonProps = {
  /** Sets the icon name, which determines which icon to display.
- `undefined` Task is actively executing and making progress.
- `undefined` Aligns the popover to the beginning edge of the anchor for left or top alignment. */
  "icon-name"?:
    | "academic-cap"
    | "add-asset"
    | "add-comment"
    | "add-grid"
    | "add-user"
    | "add"
    | "ancestors"
    | "archive"
    | "arrow-angle"
    | "arrow-both"
    | "arrow-cycle"
    | "arrow-path-rounded-square"
    | "arrow-stop"
    | "arrow"
    | "at-symbol"
    | "backspace"
    | "bar-pill-stack"
    | "bars-3-bottom-left"
    | "bars-3-bottom-right"
    | "bars-3-center-left"
    | "bars-3"
    | "bars-4"
    | "beaker"
    | "bell-slash"
    | "bell-stroke"
    | "bell"
    | "bold"
    | "book"
    | "bookmark-stroke"
    | "bookmark"
    | "bounding-box"
    | "branch"
    | "briefcase"
    | "broadcast"
    | "browser"
    | "bug"
    | "calendar"
    | "camera"
    | "cancel"
    | "caret"
    | "carets-closed-square"
    | "carousel"
    | "category-list"
    | "chart-bar"
    | "chat-bubble"
    | "chat-bubbles"
    | "check-badge"
    | "check"
    | "checklist"
    | "checkmark-circle"
    | "chevron"
    | "chip"
    | "circle-angled-line"
    | "circle-dash"
    | "circle-dot-arrows"
    | "circle-dot"
    | "circle-half"
    | "circle-rule"
    | "circle-tick"
    | "circle"
    | "clipboard"
    | "clock-circle-arrow"
    | "clock"
    | "cloud-download"
    | "cloud-upload"
    | "cloud"
    | "code"
    | "collapse-all"
    | "collapse-details"
    | "color-palette"
    | "columns"
    | "compare"
    | "computer"
    | "connect-node"
    | "connected-blocks"
    | "copy"
    | "cross-hairs"
    | "cursor-rays"
    | "cursor-ripples"
    | "data-management"
    | "delete-node"
    | "delete"
    | "doc-checkmark"
    | "dock-bottom"
    | "dock-none"
    | "dock-side"
    | "document-clipboard"
    | "document"
    | "dot-stroke"
    | "dot"
    | "double-chevron"
    | "download"
    | "drag"
    | "dropper"
    | "duplicate"
    | "edit"
    | "ellipses"
    | "envelope"
    | "exclamation-circle"
    | "exclamation-mark"
    | "exclamation-triangle"
    | "expand-all"
    | "expand-details"
    | "expression"
    | "eye-hidden"
    | "eye"
    | "face-frown"
    | "face-smile"
    | "fast-forward-10"
    | "fast-forward"
    | "film"
    | "filter-stroke"
    | "filter"
    | "flag-stroke"
    | "flag"
    | "fold"
    | "folder"
    | "fork"
    | "gear"
    | "globe-alt-stroke"
    | "globe"
    | "group-boxes"
    | "group"
    | "hand"
    | "hash"
    | "heading"
    | "home"
    | "horizontal-rule"
    | "hourglass-end"
    | "hourglass-mid"
    | "hourglass-start"
    | "hourglass"
    | "identification"
    | "image"
    | "inbox"
    | "infinity"
    | "information-circle-stroke"
    | "inspect"
    | "italic"
    | "key"
    | "keyboard"
    | "laptop-phone"
    | "layers"
    | "lifebuoy"
    | "lightbulb"
    | "lightning-bolt"
    | "link"
    | "list-ordered"
    | "list-unordered"
    | "lock"
    | "login"
    | "logout"
    | "looping-off"
    | "looping"
    | "map-drives"
    | "map-pin"
    | "map"
    | "markdown"
    | "maximize"
    | "megaphone"
    | "menu"
    | "merge"
    | "meter"
    | "minimize"
    | "minus-circle"
    | "minus"
    | "moon"
    | "more-actions"
    | "multiselect"
    | "music-note"
    | "newspaper"
    | "not-allowed"
    | "numbers"
    | "office-building"
    | "outline"
    | "paper-airplane"
    | "paper-clip"
    | "pause"
    | "pencil-square"
    | "person-2"
    | "person-3"
    | "person-circle"
    | "person"
    | "phone"
    | "picture-in-picture"
    | "pie-chart"
    | "pin"
    | "pizza-slice"
    | "placeholder"
    | "play"
    | "plug"
    | "plus-circle"
    | "plus-minus"
    | "pointer-stroke"
    | "pointer"
    | "priority-high"
    | "priority-low"
    | "priority-medium"
    | "projector"
    | "pull-close"
    | "pull-draft"
    | "pull-open"
    | "pulse"
    | "puzzle-piece"
    | "question-mark-circle-stroke"
    | "question-mark-circle"
    | "rectangle-group"
    | "rectangle-stack-horizontal"
    | "rectangle-stack-vertical"
    | "redo"
    | "refresh"
    | "reply"
    | "rewind-10"
    | "rewind"
    | "rocketship"
    | "running"
    | "scale"
    | "scissors"
    | "search"
    | "sensor"
    | "server-stack"
    | "server"
    | "shapes"
    | "share"
    | "signal-slash"
    | "signal"
    | "signpost"
    | "sort-ascending"
    | "sort-descending"
    | "soundwave"
    | "sparkles"
    | "split-horizontal"
    | "split-none"
    | "split-vertical"
    | "star-half"
    | "star-stroke"
    | "star"
    | "start"
    | "status-offline"
    | "status-online"
    | "stop-sign"
    | "stopwatch"
    | "strikethrough"
    | "sun"
    | "swatch"
    | "switch-apps"
    | "switch"
    | "table"
    | "tag"
    | "task"
    | "telescope"
    | "template"
    | "terminal"
    | "thumb-stroke"
    | "thumb"
    | "traffic-cone"
    | "transparent-box"
    | "trend-down"
    | "trend-up"
    | "trophy"
    | "truck"
    | "typography"
    | "undo"
    | "unlock"
    | "upload"
    | "video-camera"
    | "view-as-grid"
    | "volume-muted"
    | "volume"
    | "wifi"
    | "wrench"
    | "x-circle"
    | "zoom-in"
    | "zoom-out";
  /** Sets the direction of the icon.
Only supported by expand-panel/collapse-panel (horizontal axis) and arrow/caret/chevron icons (4-directions)
- `undefined` Positions the popover to the left side of the anchor element.
- `undefined` Positions the popover to the right side of the anchor element. */
  direction?: "up" | "down" | "left" | "right";
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts. */
  size?: "sm" | "md" | "lg" | "default";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container.
- `undefined` Element container is reduced to fit within inline content such as a block of text. */
  container?: "flat" | "inline" | "default";
  /** The Interaction type provides a way to indicate the intent of an interactive element. This can help users quickly understand what each interaction will do and reduce the potential for confusion or errors.
- `undefined` Increases visual weight to draw attention and highlight important elements.
- `undefined` Indicates the interaction is intended to be used for destructive actions such as deleting or removing. */
  interaction?: "emphasis" | "destructive";
  /** Indicates the current state of a toggle button that can be switched on or off. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-pressed)
- `undefined` The button is in the pressed (on) state and the associated action or setting is active.
- `undefined` The button is in the unpressed (off) state and the associated action or setting is inactive. */
  pressed?: boolean;
  /** Indicates whether collapsible content is currently visible or hidden from the user. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-expanded)
- `undefined` The associated content is expanded and visible to the user.
- `undefined` The associated content is collapsed and hidden from the user. */
  expanded?: boolean;
  /** Indicates whether the element's value can be modified by the user while remaining visible and focusable. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/readonly)
- `undefined` The element is readonly and its value cannot be changed, but can still be focused and copied.
- `undefined` The element is editable and the user can modify its value through interaction. */
  readonly?: boolean;
  /** Similar to input form, sets a button to submit a form outside its parent form.
Returns a reference to the form element if available.
https://developer.mozilla.org/en-US/docs/Web/API/ElementInternals/form */
  form?: HTMLFormElement | null | string;
  /** The name of the element, submitted as a pair with the element value as part of the form data. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-name) */
  name?: string;
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: string;
  /** Defines the button behavior when associated within an <form> element.
https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-type */
  type?: "button" | "submit" | "reset";
  /** This Boolean attribute prevents the user from interacting with the element: it cannot be pressed or focused. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-disabled)
- `undefined` The element is disabled and cannot be interacted with.
- `undefined` The element is enabled and can be interacted with. */
  disabled?: boolean;
  /** Indicates whether an element is currently chosen within a multi-option selection group. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-selected)
- `undefined` The element is selected and represents the user's current choice within the group.
- `undefined` The element is not selected and is available to be chosen by the user. */
  selected?: boolean;
  /** Indicates the element that represents the user's current location or position within a set. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-current)
- `page` - Marks the current page within a set of navigation links.
- `step` - Marks the current step within a multi-step process or workflow. */
  current?: "page" | "step";
  /** Establishing a relationship between a popover and its invoker button.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetElement */
  popoverTargetElement?: HTMLElement;
  /** The id of the element to which the popover is applied.
https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button#popovertarget */
  popovertarget?: string;
  /** The popover target action to be applied to the popover target element.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetAction */
  popovertargetaction?: "show" | "hide" | "toggle";
  /** The id of the element to which the command is applied.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  commandfor?: string;
  /** The command to be applied to the element.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  command?: string;
};

export type IconProps = {
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation.
- `undefined` Represents positive outcomes, confirmations, or constructive actions.
- `undefined` Highlights important actions or draws attention to primary interactive elements. */
  status?: "warning" | "danger" | "success" | "accent" | "default";
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts.
- `undefined` Extra small size for very small elements or very dense layouts.
- `undefined` Extra extra large size for very large elements or very sparse layouts. */
  size?: "sm" | "md" | "lg" | "xs" | "xl" | "default";
  /** Sets the direction of the icon. Only supported by expand-panel/collapse-panel (horizontal axis) and arrow/caret/chevron icons (4-directions)
- `undefined` Positions the popover to the left side of the anchor element.
- `undefined` Positions the popover to the right side of the anchor element. */
  direction?: "up" | "down" | "left" | "right" | "default";
  /** The name of the element, submitted as a pair with the element value as part of the form data. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-name)
- `undefined` Task is actively executing and making progress.
- `undefined` Aligns the popover to the beginning edge of the anchor for left or top alignment. */
  name?:
    | "academic-cap"
    | "add-asset"
    | "add-comment"
    | "add-grid"
    | "add-user"
    | "add"
    | "ancestors"
    | "archive"
    | "arrow-angle"
    | "arrow-both"
    | "arrow-cycle"
    | "arrow-path-rounded-square"
    | "arrow-stop"
    | "arrow"
    | "at-symbol"
    | "backspace"
    | "bar-pill-stack"
    | "bars-3-bottom-left"
    | "bars-3-bottom-right"
    | "bars-3-center-left"
    | "bars-3"
    | "bars-4"
    | "beaker"
    | "bell-slash"
    | "bell-stroke"
    | "bell"
    | "bold"
    | "book"
    | "bookmark-stroke"
    | "bookmark"
    | "bounding-box"
    | "branch"
    | "briefcase"
    | "broadcast"
    | "browser"
    | "bug"
    | "calendar"
    | "camera"
    | "cancel"
    | "caret"
    | "carets-closed-square"
    | "carousel"
    | "category-list"
    | "chart-bar"
    | "chat-bubble"
    | "chat-bubbles"
    | "check-badge"
    | "check"
    | "checklist"
    | "checkmark-circle"
    | "chevron"
    | "chip"
    | "circle-angled-line"
    | "circle-dash"
    | "circle-dot-arrows"
    | "circle-dot"
    | "circle-half"
    | "circle-rule"
    | "circle-tick"
    | "circle"
    | "clipboard"
    | "clock-circle-arrow"
    | "clock"
    | "cloud-download"
    | "cloud-upload"
    | "cloud"
    | "code"
    | "collapse-all"
    | "collapse-details"
    | "color-palette"
    | "columns"
    | "compare"
    | "computer"
    | "connect-node"
    | "connected-blocks"
    | "copy"
    | "cross-hairs"
    | "cursor-rays"
    | "cursor-ripples"
    | "data-management"
    | "delete-node"
    | "delete"
    | "doc-checkmark"
    | "dock-bottom"
    | "dock-none"
    | "dock-side"
    | "document-clipboard"
    | "document"
    | "dot-stroke"
    | "dot"
    | "double-chevron"
    | "download"
    | "drag"
    | "dropper"
    | "duplicate"
    | "edit"
    | "ellipses"
    | "envelope"
    | "exclamation-circle"
    | "exclamation-mark"
    | "exclamation-triangle"
    | "expand-all"
    | "expand-details"
    | "expression"
    | "eye-hidden"
    | "eye"
    | "face-frown"
    | "face-smile"
    | "fast-forward-10"
    | "fast-forward"
    | "film"
    | "filter-stroke"
    | "filter"
    | "flag-stroke"
    | "flag"
    | "fold"
    | "folder"
    | "fork"
    | "gear"
    | "globe-alt-stroke"
    | "globe"
    | "group-boxes"
    | "group"
    | "hand"
    | "hash"
    | "heading"
    | "home"
    | "horizontal-rule"
    | "hourglass-end"
    | "hourglass-mid"
    | "hourglass-start"
    | "hourglass"
    | "identification"
    | "image"
    | "inbox"
    | "infinity"
    | "information-circle-stroke"
    | "inspect"
    | "italic"
    | "key"
    | "keyboard"
    | "laptop-phone"
    | "layers"
    | "lifebuoy"
    | "lightbulb"
    | "lightning-bolt"
    | "link"
    | "list-ordered"
    | "list-unordered"
    | "lock"
    | "login"
    | "logout"
    | "looping-off"
    | "looping"
    | "map-drives"
    | "map-pin"
    | "map"
    | "markdown"
    | "maximize"
    | "megaphone"
    | "menu"
    | "merge"
    | "meter"
    | "minimize"
    | "minus-circle"
    | "minus"
    | "moon"
    | "more-actions"
    | "multiselect"
    | "music-note"
    | "newspaper"
    | "not-allowed"
    | "numbers"
    | "office-building"
    | "outline"
    | "paper-airplane"
    | "paper-clip"
    | "pause"
    | "pencil-square"
    | "person-2"
    | "person-3"
    | "person-circle"
    | "person"
    | "phone"
    | "picture-in-picture"
    | "pie-chart"
    | "pin"
    | "pizza-slice"
    | "placeholder"
    | "play"
    | "plug"
    | "plus-circle"
    | "plus-minus"
    | "pointer-stroke"
    | "pointer"
    | "priority-high"
    | "priority-low"
    | "priority-medium"
    | "projector"
    | "pull-close"
    | "pull-draft"
    | "pull-open"
    | "pulse"
    | "puzzle-piece"
    | "question-mark-circle-stroke"
    | "question-mark-circle"
    | "rectangle-group"
    | "rectangle-stack-horizontal"
    | "rectangle-stack-vertical"
    | "redo"
    | "refresh"
    | "reply"
    | "rewind-10"
    | "rewind"
    | "rocketship"
    | "running"
    | "scale"
    | "scissors"
    | "search"
    | "sensor"
    | "server-stack"
    | "server"
    | "shapes"
    | "share"
    | "signal-slash"
    | "signal"
    | "signpost"
    | "sort-ascending"
    | "sort-descending"
    | "soundwave"
    | "sparkles"
    | "split-horizontal"
    | "split-none"
    | "split-vertical"
    | "star-half"
    | "star-stroke"
    | "star"
    | "start"
    | "status-offline"
    | "status-online"
    | "stop-sign"
    | "stopwatch"
    | "strikethrough"
    | "sun"
    | "swatch"
    | "switch-apps"
    | "switch"
    | "table"
    | "tag"
    | "task"
    | "telescope"
    | "template"
    | "terminal"
    | "thumb-stroke"
    | "thumb"
    | "traffic-cone"
    | "transparent-box"
    | "trend-down"
    | "trend-up"
    | "trophy"
    | "truck"
    | "typography"
    | "undo"
    | "unlock"
    | "upload"
    | "video-camera"
    | "view-as-grid"
    | "volume-muted"
    | "volume"
    | "wifi"
    | "wrench"
    | "x-circle"
    | "zoom-in"
    | "zoom-out"
    | "default";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type InputGroupProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";
};

export type InputProps = {
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container. */
  container?: "flat" | "default";
  /** Sets the rounded visual style of the input. */
  rounded?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type JSONViewerProps = {
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: object;
  /** Indicates whether collapsible content is currently visible or hidden from the user. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-expanded)
- `undefined` The associated content is expanded and visible to the user.
- `undefined` The associated content is collapsed and hidden from the user. */
  expanded?: boolean;
  /**  */
  expandedAll?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type LogoProps = {
  /** Defines a base color from the theme color palette */
  color?:
    | "red-cardinal"
    | "gray-slate"
    | "gray-denim"
    | "blue-indigo"
    | "blue-cobalt"
    | "blue-sky"
    | "teal-cyan"
    | "green-mint"
    | "teal-seafoam"
    | "green-grass"
    | "yellow-amber"
    | "orange-pumpkin"
    | "red-tomato"
    | "pink-magenta"
    | "purple-plum"
    | "purple-violet"
    | "purple-lavender"
    | "pink-rose"
    | "green-jade"
    | "lime-pear"
    | "yellow-nova"
    | "brand-green";
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts. */
  size?: "sm" | "md" | "lg" | "default";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type MenuItemProps = {
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation. */
  status?: "danger";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Indicates the current state of a toggle button that can be switched on or off. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-pressed)
- `undefined` The button is in the pressed (on) state and the associated action or setting is active.
- `undefined` The button is in the unpressed (off) state and the associated action or setting is inactive. */
  pressed?: boolean;
  /** Indicates whether collapsible content is currently visible or hidden from the user. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-expanded)
- `undefined` The associated content is expanded and visible to the user.
- `undefined` The associated content is collapsed and hidden from the user. */
  expanded?: boolean;
  /** Indicates whether the element's value can be modified by the user while remaining visible and focusable. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/readonly)
- `undefined` The element is readonly and its value cannot be changed, but can still be focused and copied.
- `undefined` The element is editable and the user can modify its value through interaction. */
  readonly?: boolean;
  /** Similar to input form, sets a button to submit a form outside its parent form.
Returns a reference to the form element if available.
https://developer.mozilla.org/en-US/docs/Web/API/ElementInternals/form */
  form?: HTMLFormElement | null | string;
  /** The name of the element, submitted as a pair with the element value as part of the form data. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-name) */
  name?: string;
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: string;
  /** Defines the button behavior when associated within an <form> element.
https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-type */
  type?: "button" | "submit" | "reset";
  /** This Boolean attribute prevents the user from interacting with the element: it cannot be pressed or focused. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-disabled)
- `undefined` The element is disabled and cannot be interacted with.
- `undefined` The element is enabled and can be interacted with. */
  disabled?: boolean;
  /** Indicates whether an element is currently chosen within a multi-option selection group. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-selected)
- `undefined` The element is selected and represents the user's current choice within the group.
- `undefined` The element is not selected and is available to be chosen by the user. */
  selected?: boolean;
  /** Indicates the element that represents the user's current location or position within a set. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-current)
- `page` - Marks the current page within a set of navigation links.
- `step` - Marks the current step within a multi-step process or workflow. */
  current?: "page" | "step";
  /** Establishing a relationship between a popover and its invoker button.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetElement */
  popoverTargetElement?: HTMLElement;
  /** The id of the element to which the popover is applied.
https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button#popovertarget */
  popovertarget?: string;
  /** The popover target action to be applied to the popover target element.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetAction */
  popovertargetaction?: "show" | "hide" | "toggle";
  /** The id of the element to which the command is applied.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  commandfor?: string;
  /** The command to be applied to the element.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  command?: string;
};

export type MenuProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /**  */
  items?: MenuItem[];
};

export type MonthProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type NotificationGroupProps = {
  /** Provides the element that the popover should position relative to. Anchor can accept a idref string within the same render root or a HTMLElement DOM reference. */
  anchor?: string | HTMLElement;
  /** Determines the position of an element along both inline and block axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Box_alignment_in_grid_layout#the_two_axes_of_a_grid_layout) */
  position?: string;
  /** Determines the alignment of the popover relative to the provided anchor element.
- `undefined` Aligns the popover to the beginning edge of the anchor for left or top alignment.
- `undefined` Aligns the popover to the ending edge of the anchor for right or bottom alignment.
- `undefined` Centers the popover along the anchor's edge for balanced positioning. */
  alignment?: "start" | "end" | "center";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type NotificationProps = {
  /** Provides the element that the popover should position relative to. Anchor can accept a idref string within the same render root or a HTMLElement DOM reference. */
  anchor?: string | HTMLElement;
  /** Defines what element triggers an `open` interaction event. A trigger can accept a idref string within the same render root or a HTMLElement DOM reference. */
  trigger?: string | HTMLElement;
  /** Determines the position of an element along both inline and block axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Box_alignment_in_grid_layout#the_two_axes_of_a_grid_layout)
- `undefined` Centers the popover along the anchor's edge for balanced positioning.
- `undefined` Positions the popover above the anchor element.
- `undefined` Positions the popover below the anchor element.
- `undefined` Positions the popover to the left side of the anchor element.
- `undefined` Positions the popover to the right side of the anchor element. */
  position?: "center" | "top" | "bottom" | "left" | "right";
  /** Determines the alignment of the popover relative to the provided anchor element.
- `undefined` Aligns the popover to the beginning edge of the anchor for left or top alignment.
- `undefined` Aligns the popover to the ending edge of the anchor for right or bottom alignment.
- `undefined` Centers the popover along the anchor's edge for balanced positioning. */
  alignment?: "start" | "end" | "center";
  /** Determines if popover visibility behavior should be automatically controlled by the trigger. */
  "behavior-trigger"?: boolean;
  /** Indicates whether the element can be dismissed or closed by the user.
- `undefined` The element displays a close control and can be dismissed by the user.
- `undefined` The element cannot be closed by the user and requires programmatic dismissal. */
  closable?: boolean;
  /** A delayed `close` event will occur determined from the provided millisecond value. */
  "close-timeout"?: number;
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Highlights important actions or draws attention to primary interactive elements.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation. */
  status?: "accent" | "warning" | "success" | "danger";
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container. */
  container?: "flat" | "default";
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /**  */
  inline?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";

  /** Dispatched when the notification is closed. */
  onclose?: (e: CustomEvent<CustomEvent>) => void;
  /** Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event) */
  onbeforetoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event) */
  ontoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched when the notification is opened. */
  onopen?: (e: CustomEvent<never>) => void;
};

export type PageHeaderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type PageLoaderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type PagePanelContentProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type PagePanelFooterProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /**  */
  slot?: string;
};

export type PagePanelHeaderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /**  */
  slot?: string;
};

export type PagePanelProps = {
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts. */
  size?: "sm" | "md" | "lg" | "default";
  /** Indicates whether the element can be dismissed or closed by the user.
- `undefined` The element displays a close control and can be dismissed by the user.
- `undefined` The element cannot be closed by the user and requires programmatic dismissal. */
  closable?: boolean;
  /** Determines if a expandable button should render within page panel. */
  expandable?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";

  /**  */
  onopen?: (e: CustomEvent<never>) => void;
  /**  */
  onclose?: (e: CustomEvent<never>) => void;
};

export type PageProps = {
  /** Enables the page to use the document content scroll rather than its internal fixed scroll. */
  "document-scroll"?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type PaginationProps = {
  /** The number of items per page. */
  step?: number;
  /** The array of custom step-size. */
  stepSizes?: array;
  /** The total number of items. */
  items?: number;
  /** Whether or not the pagination is skippable to start/end. */
  skippable?: boolean;
  /** Whether or not the step selector is disabled. */
  "disable-step"?: boolean;
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container.
- `undefined` Element container is reduced to fit within inline content such as a block of text. */
  container?: "flat" | "inline" | "default";
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: number;
  /**  */
  "onstep-change"?: (e: CustomEvent<CustomEvent>) => void;
  /** emits when the last page is active */
  "onlast-page"?: (e: CustomEvent<CustomEvent>) => void;
  /** emits when the first page is active */
  "onfirst-page"?: (e: CustomEvent<CustomEvent>) => void;
  /** emits when the value (page) has changed */
  oninput?: (e: CustomEvent<never>) => void;
  /** emits when the value (page) has changed */
  onchange?: (e: CustomEvent<never>) => void;
};

export type PanelHeaderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type PanelContentProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type PanelFooterProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type PanelProps = {
  /** Indicates whether collapsible content is currently visible or hidden from the user. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-expanded)
- `undefined` The associated content is expanded and visible to the user.
- `undefined` The associated content is collapsed and hidden from the user. */
  expanded?: boolean;
  /** Indicates whether the element can be dismissed or closed by the user.
- `undefined` The element displays a close control and can be dismissed by the user.
- `undefined` The element cannot be closed by the user and requires programmatic dismissal. */
  closable?: boolean;
  /** Determines whether or not the panel should handle auto-closing behavior vs. defaults to off. */
  "behavior-expand"?: boolean;
  /** Sets the proper collapse icon and collapse animation, based on what side of the page the panel will be used.
- `undefined` Positions the popover to the left side of the anchor element.
- `undefined` Positions the popover to the right side of the anchor element. */
  side?: "left" | "right";
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";

  /** Dispatched when the panel is opened. */
  onopen?: (e: CustomEvent<never>) => void;
  /** Dispatched when the panel is closed. */
  onclose?: (e: CustomEvent<never>) => void;
};

export type PasswordProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type PreferencesInputProps = {
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: object;
  /** emits when the value has changed */
  oninput?: (e: CustomEvent<never>) => void;
  /** emits when the value has changed */
  onchange?: (e: CustomEvent<never>) => void;
};

export type ProgressBarProps = {
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: number | "default";
  /** The `max` property sets the highest value that `value` will be scaled to. */
  max?: number;
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Highlights important actions or draws attention to primary interactive elements.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation. */
  status?: "accent" | "warning" | "success" | "danger";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type ProgressRingProps = {
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: number | "default";
  /** The `max` value of the progress ring that the `value` is proportionaly scaled to. */
  max?: number;
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Highlights important actions or draws attention to primary interactive elements.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation. */
  status?: "accent" | "warning" | "success" | "danger" | "neutral" | "default";
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts.
- `undefined` Extra small size for very small elements or very dense layouts.
- `undefined` Extra extra large size for very large elements or very sparse layouts. */
  size?: "sm" | "md" | "lg" | "xxs" | "xs" | "xl" | "default";
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type ProgressiveFilterChipProps = {
  /** Indicates whether the element can be dismissed or closed by the user.
- `undefined` The element displays a close control and can be dismissed by the user.
- `undefined` The element cannot be closed by the user and requires programmatic dismissal. */
  closable?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";

  /** Dispatched when the filter chip is closed. */
  onclose?: (e: CustomEvent<never>) => void;
};

export type PulseProps = {
  /** Controls the visual scale of an element to match its importance and available space.
- `undefined` Compact size for dense layouts or secondary elements with less visual prominence.
- `undefined` Standard size that works well in most contexts and provides balanced visibility.
- `undefined` Larger size for emphasizing important elements or improving touch targets in spacious layouts.
- `undefined` Extra small size for very small elements or very dense layouts. */
  size?: "sm" | "md" | "lg" | "xs" | "default";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Highlights important actions or draws attention to primary interactive elements.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation. */
  status?: "accent" | "warning" | "danger" | "default";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type RadioGroupProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";
};

export type RadioProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type RangeProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type ResizeHandleProps = {
  /** Controls the directional flow of the element's layout and interaction pattern.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content in a vertical stack with block-level spacing. */
  orientation?: "horizontal" | "vertical" | "default";
  /** Determines the minimum resize value. */
  min?: number;
  /** Determines the maximum resize value. */
  max?: number;
  /** Determines the value step change. */
  step?: number;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: string;
  /** Dispatched when the resize handle is double clicked. */
  ontoggle?: (e: CustomEvent<CustomEvent>) => void;
};

export type SearchProps = {
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container. */
  container?: "flat" | "default";
  /** Sets the rounded visual style of the input. */
  rounded?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type SelectProps = {
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container.
- `undefined` Element container is reduced to fit within inline content such as a block of text. */
  container?: "flat" | "inline" | "default";
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type SkeletonProps = {
  /** The effect of the skeleton */
  effect?: "shimmer" | "pulse";
  /** The shape of the skeleton */
  shape?: "round" | "pill";
  /** Whether the skeleton is hidden */
  hidden?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type SortButtonProps = {
  /** The current sort value, can be ascending, descending, or none. */
  sort?: "ascending" | "descending" | "none";
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Indicates the current state of a toggle button that can be switched on or off. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-pressed)
- `undefined` The button is in the pressed (on) state and the associated action or setting is active.
- `undefined` The button is in the unpressed (off) state and the associated action or setting is inactive. */
  pressed?: boolean;
  /** Indicates whether collapsible content is currently visible or hidden from the user. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-expanded)
- `undefined` The associated content is expanded and visible to the user.
- `undefined` The associated content is collapsed and hidden from the user. */
  expanded?: boolean;
  /** Indicates whether the element's value can be modified by the user while remaining visible and focusable. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/readonly)
- `undefined` The element is readonly and its value cannot be changed, but can still be focused and copied.
- `undefined` The element is editable and the user can modify its value through interaction. */
  readonly?: boolean;
  /** Similar to input form, sets a button to submit a form outside its parent form.
Returns a reference to the form element if available.
https://developer.mozilla.org/en-US/docs/Web/API/ElementInternals/form */
  form?: HTMLFormElement | null | string;
  /** The name of the element, submitted as a pair with the element value as part of the form data. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-name) */
  name?: string;
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: string;
  /** Defines the button behavior when associated within an <form> element.
https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-type */
  type?: "button" | "submit" | "reset";
  /** This Boolean attribute prevents the user from interacting with the element: it cannot be pressed or focused. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-disabled)
- `undefined` The element is disabled and cannot be interacted with.
- `undefined` The element is enabled and can be interacted with. */
  disabled?: boolean;
  /** Indicates whether an element is currently chosen within a multi-option selection group. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-selected)
- `undefined` The element is selected and represents the user's current choice within the group.
- `undefined` The element is not selected and is available to be chosen by the user. */
  selected?: boolean;
  /** Indicates the element that represents the user's current location or position within a set. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-current)
- `page` - Marks the current page within a set of navigation links.
- `step` - Marks the current step within a multi-step process or workflow. */
  current?: "page" | "step";
  /** Establishing a relationship between a popover and its invoker button.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetElement */
  popoverTargetElement?: HTMLElement;
  /** The id of the element to which the popover is applied.
https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button#popovertarget */
  popovertarget?: string;
  /** The popover target action to be applied to the popover target element.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetAction */
  popovertargetaction?: "show" | "hide" | "toggle";
  /** The id of the element to which the command is applied.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  commandfor?: string;
  /** The command to be applied to the element.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  command?: string;

  /** Dispatched when the sort button is clicked, returns the current sort value and the next sort value. */
  onsort?: (e: CustomEvent<CustomEvent>) => void;
};

export type StarRatingProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type StepsItemProps = {
  /** Indicates whether an element is currently chosen within a multi-option selection group. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-selected)
- `undefined` The element is selected and represents the user's current choice within the group.
- `undefined` The element is not selected and is available to be chosen by the user. */
  selected?: boolean;
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Highlights important actions or draws attention to primary interactive elements.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation.
- `undefined` Represents positive outcomes, confirmations, or constructive actions.
- `undefined` Task is awaiting approval, user input, or external conditions before proceeding. */
  status?: "accent" | "danger" | "success" | "pending" | "default";
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element container is optimized for small, summarized or contained spaces. */
  container?: "condensed" | "default";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Indicates the current state of a toggle button that can be switched on or off. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-pressed)
- `undefined` The button is in the pressed (on) state and the associated action or setting is active.
- `undefined` The button is in the unpressed (off) state and the associated action or setting is inactive. */
  pressed?: boolean;
  /** Indicates whether collapsible content is currently visible or hidden from the user. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-expanded)
- `undefined` The associated content is expanded and visible to the user.
- `undefined` The associated content is collapsed and hidden from the user. */
  expanded?: boolean;
  /** Indicates whether the element's value can be modified by the user while remaining visible and focusable. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/readonly)
- `undefined` The element is readonly and its value cannot be changed, but can still be focused and copied.
- `undefined` The element is editable and the user can modify its value through interaction. */
  readonly?: boolean;
  /** Similar to input form, sets a button to submit a form outside its parent form.
Returns a reference to the form element if available.
https://developer.mozilla.org/en-US/docs/Web/API/ElementInternals/form */
  form?: HTMLFormElement | null | string;
  /** The name of the element, submitted as a pair with the element value as part of the form data. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-name) */
  name?: string;
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: string;
  /** Defines the button behavior when associated within an <form> element.
https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-type */
  type?: "button" | "submit" | "reset";
  /** This Boolean attribute prevents the user from interacting with the element: it cannot be pressed or focused. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-disabled)
- `undefined` The element is disabled and cannot be interacted with.
- `undefined` The element is enabled and can be interacted with. */
  disabled?: boolean;
  /** Indicates the element that represents the user's current location or position within a set. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-current)
- `page` - Marks the current page within a set of navigation links.
- `step` - Marks the current step within a multi-step process or workflow. */
  current?: "page" | "step";
  /** Establishing a relationship between a popover and its invoker button.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetElement */
  popoverTargetElement?: HTMLElement;
  /** The id of the element to which the popover is applied.
https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button#popovertarget */
  popovertarget?: string;
  /** The popover target action to be applied to the popover target element.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetAction */
  popovertargetaction?: "show" | "hide" | "toggle";
  /** The id of the element to which the command is applied.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  commandfor?: string;
  /** The command to be applied to the element.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  command?: string;
};

export type StepsProps = {
  /** Determines whether or not the steps should display in a vertical layout vs. defaulting to horizontal. */
  vertical?: boolean;
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element container is optimized for small, summarized or contained spaces. */
  container?: "condensed" | "default";
  /** Determines whether or not the steps should handle selection behavior vs. defaults to off. */
  "behavior-select"?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type SwitchProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type TabsItemProps = {
  /** Indicates whether an element is currently chosen within a multi-option selection group. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-selected)
- `undefined` The element is selected and represents the user's current choice within the group.
- `undefined` The element is not selected and is available to be chosen by the user. */
  selected?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Indicates the current state of a toggle button that can be switched on or off. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-pressed)
- `undefined` The button is in the pressed (on) state and the associated action or setting is active.
- `undefined` The button is in the unpressed (off) state and the associated action or setting is inactive. */
  pressed?: boolean;
  /** Indicates whether collapsible content is currently visible or hidden from the user. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-expanded)
- `undefined` The associated content is expanded and visible to the user.
- `undefined` The associated content is collapsed and hidden from the user. */
  expanded?: boolean;
  /** Indicates whether the element's value can be modified by the user while remaining visible and focusable. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/readonly)
- `undefined` The element is readonly and its value cannot be changed, but can still be focused and copied.
- `undefined` The element is editable and the user can modify its value through interaction. */
  readonly?: boolean;
  /** Similar to input form, sets a button to submit a form outside its parent form.
Returns a reference to the form element if available.
https://developer.mozilla.org/en-US/docs/Web/API/ElementInternals/form */
  form?: HTMLFormElement | null | string;
  /** The name of the element, submitted as a pair with the element value as part of the form data. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-name) */
  name?: string;
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: string;
  /** Defines the button behavior when associated within an <form> element.
https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-type */
  type?: "button" | "submit" | "reset";
  /** This Boolean attribute prevents the user from interacting with the element: it cannot be pressed or focused. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-disabled)
- `undefined` The element is disabled and cannot be interacted with.
- `undefined` The element is enabled and can be interacted with. */
  disabled?: boolean;
  /** Indicates the element that represents the user's current location or position within a set. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-current)
- `page` - Marks the current page within a set of navigation links.
- `step` - Marks the current step within a multi-step process or workflow. */
  current?: "page" | "step";
  /** Establishing a relationship between a popover and its invoker button.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetElement */
  popoverTargetElement?: HTMLElement;
  /** The id of the element to which the popover is applied.
https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button#popovertarget */
  popovertarget?: string;
  /** The popover target action to be applied to the popover target element.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetAction */
  popovertargetaction?: "show" | "hide" | "toggle";
  /** The id of the element to which the command is applied.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  commandfor?: string;
  /** The command to be applied to the element.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  command?: string;
};

export type TabsProps = {
  /** Determines whether or not the tabs should display in a vertical layout vs. defaulting to horizontal. */
  vertical?: boolean;
  /** Determines whether or not the tabs should display a border on selected items vs. defaults to show border. */
  borderless?: boolean;
  /** Determines whether or not the tabs should handle selection behavior vs. defaults to off. */
  "behavior-select"?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type TagProps = {
  /** Indicates whether the element can be dismissed or closed by the user.
- `undefined` The element displays a close control and can be dismissed by the user.
- `undefined` The element cannot be closed by the user and requires programmatic dismissal. */
  closable?: boolean;
  /** Defines a base color from the theme color palette */
  color?:
    | "red-cardinal"
    | "gray-slate"
    | "gray-denim"
    | "blue-indigo"
    | "blue-cobalt"
    | "blue-sky"
    | "teal-cyan"
    | "green-mint"
    | "teal-seafoam"
    | "green-grass"
    | "yellow-amber"
    | "orange-pumpkin"
    | "red-tomato"
    | "pink-magenta"
    | "purple-plum"
    | "purple-violet"
    | "purple-lavender"
    | "pink-rose"
    | "green-jade"
    | "lime-pear"
    | "yellow-nova"
    | "brand-green";
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Increases visual weight to draw attention and highlight important elements. */
  prominence?: "emphasis" | "default";
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Indicates the current state of a toggle button that can be switched on or off. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-pressed)
- `undefined` The button is in the pressed (on) state and the associated action or setting is active.
- `undefined` The button is in the unpressed (off) state and the associated action or setting is inactive. */
  pressed?: boolean;
  /** Indicates whether collapsible content is currently visible or hidden from the user. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-expanded)
- `undefined` The associated content is expanded and visible to the user.
- `undefined` The associated content is collapsed and hidden from the user. */
  expanded?: boolean;
  /** Indicates whether the element's value can be modified by the user while remaining visible and focusable. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/readonly)
- `undefined` The element is readonly and its value cannot be changed, but can still be focused and copied.
- `undefined` The element is editable and the user can modify its value through interaction. */
  readonly?: boolean;
  /** Similar to input form, sets a button to submit a form outside its parent form.
Returns a reference to the form element if available.
https://developer.mozilla.org/en-US/docs/Web/API/ElementInternals/form */
  form?: HTMLFormElement | null | string;
  /** The name of the element, submitted as a pair with the element value as part of the form data. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-name) */
  name?: string;
  /** Defines the value associated with the element's name when it's submitted with the form data. This value is passed to the server in params when the form is submitted using this button. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value) */
  value?: string;
  /** Defines the button behavior when associated within an <form> element.
https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attr-type */
  type?: "button" | "submit" | "reset";
  /** This Boolean attribute prevents the user from interacting with the element: it cannot be pressed or focused. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-disabled)
- `undefined` The element is disabled and cannot be interacted with.
- `undefined` The element is enabled and can be interacted with. */
  disabled?: boolean;
  /** Indicates whether an element is currently chosen within a multi-option selection group. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-selected)
- `undefined` The element is selected and represents the user's current choice within the group.
- `undefined` The element is not selected and is available to be chosen by the user. */
  selected?: boolean;
  /** Indicates the element that represents the user's current location or position within a set. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-current)
- `page` - Marks the current page within a set of navigation links.
- `step` - Marks the current step within a multi-step process or workflow. */
  current?: "page" | "step";
  /** Establishing a relationship between a popover and its invoker button.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetElement */
  popoverTargetElement?: HTMLElement;
  /** The id of the element to which the popover is applied.
https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button#popovertarget */
  popovertarget?: string;
  /** The popover target action to be applied to the popover target element.
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/popoverTargetAction */
  popovertargetaction?: "show" | "hide" | "toggle";
  /** The id of the element to which the command is applied.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  commandfor?: string;
  /** The command to be applied to the element.
https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API */
  command?: string;
};

export type TextareaProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type TimeProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type ToastProps = {
  /** Provides the element that the popover should position relative to. Anchor can accept a idref string within the same render root or a HTMLElement DOM reference. */
  anchor?: string | HTMLElement;
  /** Defines what element triggers an `open` interaction event. A trigger can accept a idref string within the same render root or a HTMLElement DOM reference. */
  trigger?: string | HTMLElement;
  /** Determines the position of an element along both inline and block axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Box_alignment_in_grid_layout#the_two_axes_of_a_grid_layout)
- `undefined` Centers the popover along the anchor's edge for balanced positioning.
- `undefined` Positions the popover above the anchor element.
- `undefined` Positions the popover below the anchor element.
- `undefined` Positions the popover to the left side of the anchor element.
- `undefined` Positions the popover to the right side of the anchor element. */
  position?: "center" | "top" | "bottom" | "left" | "right";
  /** Determines the alignment of the popover relative to the provided anchor element.
- `undefined` Aligns the popover to the beginning edge of the anchor for left or top alignment.
- `undefined` Aligns the popover to the ending edge of the anchor for right or bottom alignment.
- `undefined` Centers the popover along the anchor's edge for balanced positioning. */
  alignment?: "start" | "end" | "center";
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";
  /** Determines if popover visibility behavior should be automatically controlled by the trigger. */
  "behavior-trigger"?: boolean;
  /** Indicates whether the element can be dismissed or closed by the user.
- `undefined` The element displays a close control and can be dismissed by the user.
- `undefined` The element cannot be closed by the user and requires programmatic dismissal. */
  closable?: boolean;
  /** A delayed `close` event will occur determined from the provided millisecond value. */
  "close-timeout"?: number;
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive.
- `undefined` Highlights important actions or draws attention to primary interactive elements.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions.
- `undefined` Signals destructive or irreversible actions that need extra attention and confirmation. */
  status?: "accent" | "warning" | "success" | "danger" | "muted";
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";

  /** Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event) */
  onbeforetoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event) */
  ontoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched when the toast is opened. */
  onopen?: (e: CustomEvent<never>) => void;
  /** Dispatched when the toast is closed. */
  onclose?: (e: CustomEvent<never>) => void;
};

export type ToggletipFooterProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type ToggletipHeaderProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type ToggletipProps = {
  /** Provides the element that the popover should position relative to. Anchor can accept a idref string within the same render root or a HTMLElement DOM reference. */
  anchor?: string | HTMLElement;
  /** Defines what element triggers an `open` interaction event. A trigger can accept a idref string within the same render root or a HTMLElement DOM reference. */
  trigger?: string | HTMLElement;
  /** Determines the position of an element along both inline and block axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Box_alignment_in_grid_layout#the_two_axes_of_a_grid_layout)
- `undefined` Centers the popover along the anchor's edge for balanced positioning.
- `undefined` Positions the popover above the anchor element.
- `undefined` Positions the popover below the anchor element.
- `undefined` Positions the popover to the left side of the anchor element.
- `undefined` Positions the popover to the right side of the anchor element. */
  position?: "center" | "top" | "bottom" | "left" | "right";
  /** Determines the alignment of the popover relative to the provided anchor element.
- `undefined` Aligns the popover to the beginning edge of the anchor for left or top alignment.
- `undefined` Aligns the popover to the ending edge of the anchor for right or bottom alignment.
- `undefined` Centers the popover along the anchor's edge for balanced positioning. */
  alignment?: "start" | "end" | "center";
  /** Determines if popover visibility behavior should be automatically controlled by the trigger. */
  "behavior-trigger"?: boolean;
  /** Indicates whether the element can be dismissed or closed by the user.
- `undefined` The element displays a close control and can be dismissed by the user.
- `undefined` The element cannot be closed by the user and requires programmatic dismissal. */
  closable?: boolean;
  /** Determines if an arrow should be rendered. */
  arrow?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /**  */
  popoverArrow?: HTMLElement;
  /** Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event) */
  onbeforetoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event) */
  ontoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched when the toggletip is opened. */
  onopen?: (e: CustomEvent<never>) => void;
  /** Dispatched when the toggletip is closed. */
  onclose?: (e: CustomEvent<never>) => void;
};

export type ToolbarProps = {
  /** Demonstrates different container styles to accommodate various visual weight and context.
- `undefined` Element has white space bounds but reduced visual container.
- `undefined` Element container is optimized for embedding or being inset inside another containing element.
- `undefined` Element container is optimized for filling its container bounds. */
  container?: "flat" | "inset" | "full" | "default";
  /** Determines the primary content overflow behavior. */
  content?: "scroll" | "wrap" | "default";
  /** Controls the directional flow of the element's layout and interaction pattern.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content in a vertical stack with block-level spacing. */
  orientation?: "horizontal" | "vertical" | "default";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Highlights important actions or draws attention to primary interactive elements. */
  status?: "accent";
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type TooltipProps = {
  /** Provides the element that the popover should position relative to. Anchor can accept a idref string within the same render root or a HTMLElement DOM reference. */
  anchor?: string | HTMLElement;
  /** Defines what element triggers an `open` interaction event. A trigger can accept a idref string within the same render root or a HTMLElement DOM reference. */
  trigger?: string | HTMLElement;
  /** Determines the position of an element along both inline and block axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Box_alignment_in_grid_layout#the_two_axes_of_a_grid_layout)
- `undefined` Centers the popover along the anchor's edge for balanced positioning.
- `undefined` Positions the popover above the anchor element.
- `undefined` Positions the popover below the anchor element.
- `undefined` Positions the popover to the left side of the anchor element.
- `undefined` Positions the popover to the right side of the anchor element. */
  position?: "center" | "top" | "bottom" | "left" | "right";
  /** Determines the alignment of the popover relative to the provided anchor element.
- `undefined` Aligns the popover to the beginning edge of the anchor for left or top alignment.
- `undefined` Aligns the popover to the ending edge of the anchor for right or bottom alignment.
- `undefined` Centers the popover along the anchor's edge for balanced positioning. */
  alignment?: "start" | "end" | "center";
  /** Determines if popover visibility behavior should be automatically controlled by the trigger. */
  "behavior-trigger"?: boolean;
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  status?: "muted";
  /** A delayed `open` event will occur determined from the provided millisecond value. */
  "open-delay"?: number;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /**  */
  popoverArrow?: HTMLElement;
  /** Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event) */
  onbeforetoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event) */
  ontoggle?: (e: CustomEvent<never>) => void;
  /** Dispatched when the tooltip is opened. */
  onopen?: (e: CustomEvent<never>) => void;
  /** Dispatched when the tooltip is closed. */
  onclose?: (e: CustomEvent<never>) => void;
};

export type TreeNodeProps = {
  /** Indicates whether collapsible content is currently visible or hidden from the user. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-expanded)
- `undefined` The associated content is expanded and visible to the user.
- `undefined` The associated content is collapsed and hidden from the user. */
  expanded?: boolean;
  /** Indicates whether an element is currently chosen within a multi-option selection group. [MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-selected)
- `undefined` The element is selected and represents the user's current choice within the group.
- `undefined` The element is not selected and is available to be chosen by the user. */
  selected?: boolean;
  /** Determines whether a node can be expandable. Expandable by default if slotted nodes exist. */
  expandable?: boolean;
  /** Determines whether a node can be in a selected state. Nodes can be in a single or multi select state. */
  selectable?: "single" | "multi";
  /** Determines the highlighted state of the element. Highlighted states are for non-interactive selections where nodes may be related to other selected portions of the UI. */
  highlighted?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /**  */
  indeterminate?: boolean;
  /**  */
  behaviorExpand?: boolean;
  /**  */
  behaviorSelect?: boolean;
  /** Dispatched when the node is opened. */
  onopen?: (e: CustomEvent<never>) => void;
  /** Dispatched when the node is closed. */
  onclose?: (e: CustomEvent<never>) => void;
};

export type TreeProps = {
  /** Determines whether all nodes can be in a selected state. Nodes can be in a single or multi select state. */
  selectable?: "single" | "multi";
  /** Determines whether or not the tree nodes should handle auto-expanding behavior. */
  "behavior-expand"?: boolean;
  /** Determines whether or not the tree nodes should handle auto-select behavior. */
  "behavior-select"?: boolean;
  /** Determines if node depth border is rendered. */
  border?: boolean;
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
};

export type WeekProps = {
  /** @deprecated - not supported on custom element tags */
  "nve-layout"?: "disallowed";
  /** @deprecated - not supported on custom element tags */
  "nve-text"?: "disallowed";
  /** Communicates the intent and semantic meaning of an element to help users understand the outcome of their actions.
- `undefined` Indicates cautionary actions that require careful consideration before proceeding.
- `undefined` Represents positive outcomes, confirmations, or constructive actions. */
  status?: "warning" | "error" | "success" | "disabled";
  /** Controls the directional arrangement and spacing behavior of the element's content.
- `undefined` Arranges content in a vertical stack with block-level spacing.
- `undefined` Arranges content vertically with compact inline spacing for dense layouts.
- `undefined` Arranges content in a horizontal row with block-level spacing.
- `undefined` Arranges content horizontally with compact inline spacing. */
  layout?: "vertical" | "vertical-inline" | "horizontal" | "horizontal-inline";
  /** Sets the input to match the width of the active text content of the control value. Only applicable to vertical input box type controls (input, select) */
  "fit-text"?: boolean;
  /** Sets the input to match native default content block */
  "fit-content"?: boolean;
  /** Enables internal string values to be updated for internationalization. */
  i18n?: string;
  /** Controls the visual prominence to establish hierarchy and guide user attention.
- `undefined` Reduces visual weight for supporting content that should remain subtle and unobtrusive. */
  prominence?: "muted";

  /**  */
  onreset?: (e: CustomEvent<CustomEvent>) => void;
};

export type CustomElements = {
  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - **prefix** - undefined
   * - **suffix** - undefined
   *
   * ### **CSS Properties:**
   *  - **--cursor** - undefined _(default: undefined)_
   */
  "nve-accordion-header": Partial<AccordionHeaderProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - This is a default/unnamed slot for accordion content content
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   */
  "nve-accordion-content": Partial<AccordionContentProps & BaseProps & BaseEvents>;

  /**
   * An accordion is a vertical stack of interactive headings used to toggle the display of further information.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - This is a default/unnamed slot for accordion content
   * - **icon-button** - icon elements to display for expand/collapse
   * - **header** - header element (Use `accordion-header` or custom content)
   * - **content** - content element (Use `accordion-content` or custom content)
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--header-padding** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--transition** - undefined _(default: undefined)_
   */
  "nve-accordion": Partial<AccordionProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   */
  "nve-accordion-group": Partial<AccordionGroupProps & BaseProps & BaseEvents>;

  /**
   * @deprecated true
   *
   * An alert banner is an element that displays a brief, important message outside the context of the current page.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for nve-alert
   *
   * ### **CSS Properties:**
   *  - **--gap** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   */
  "nve-alert-banner": Partial<AlertBannerProps & BaseProps & BaseEvents>;

  /**
   * An alert group is an element that displays a group of related and important messages in a way that attracts the user's attention without interrupting the user's task.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for nve-alert
   *
   * ### **CSS Properties:**
   *  - **--gap** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   */
  "nve-alert-group": Partial<AlertGroupProps & BaseProps & BaseEvents>;

  /**
   * Alert is an element that displays a brief, important message in a way that attracts the user's attention without interrupting the user's task.
   * ---
   *
   *
   * ### **Events:**
   *  - **close** - Dispatched when the alert is closed within a alert group.
   *
   * ### **Slots:**
   *  - **icon** - Icon slot is placed on the left side of the alert. Icons are typically used to represent the alert's status.
   * - **prefix** - Prefix slot is placed between the icon and the content. Prefixes are typically used to represent the alert's status.
   * - **actions** - Actions are placed on the right side of the alert. Actions are typically buttons, but can also be links. Actions should be used for actions that the user can take to resolve the alert.
   * - **content** - Content for large overflow text.
   * - _default_ - Default content placed inside of the alert.
   *
   * ### **CSS Properties:**
   *  - **--gap** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--icon-color** - undefined _(default: undefined)_
   * - **--icon-size** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--justify-content** - undefined _(default: undefined)_
   * - **--align-items** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   * - **--text-transform** - undefined _(default: undefined)_
   */
  "nve-alert": Partial<AlertProps & BaseProps & BaseEvents>;

  /**
   * @deprecated use `nve-page-header` instead
   *
   * An element that appears across the top of all pages containing the application name and primary navigation.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - Use the default slot in `logo` to create an app logo badge within the app header. Include a `<span>` element inside `app-header` to change the default application title.
   * - **title** - undefined
   * - **nav-items** - For `button` and `icon-button` elements used for navigation behavior. Use the `active` attribute to indicate the current page.
   * - **nav-actions** - For `icon-button` elements. This will place them in the section of the app header where supplemental actions are located.
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--border-bottom** - undefined _(default: undefined)_
   */
  "nve-app-header": Partial<AppHeaderProps & BaseProps & BaseEvents>;

  /**
   * An avatar group displays a collection of user avatars in a compact and organized layout, showcasing multiple participants or contributors in a space-efficient way.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   */
  "nve-avatar-group": Partial<AvatarGroupProps & BaseProps & BaseEvents>;

  /**
   * Avatar represents a user/bot within a UI. Typically with text or image content.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   */
  "nve-avatar": Partial<AvatarProps & BaseProps & BaseEvents>;

  /**
   * A visual indicator that communicates a status description of an associated component. Status badges use short text, color, and icons for quick recognition and are placed near the relevant content.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   * - **prefix-icon** - slot for prefix icon
   * - **suffix-icon** - slot for suffix icon
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--icon-color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--text-transform** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   */
  "nve-badge": Partial<BadgeProps & BaseProps & BaseEvents>;

  /**
   * Breadcrumb is a component that can help users establish their location while navigating a website with complex URLs and navigation paths.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for `nve-button` and anchor elements
   *
   * ### **CSS Properties:**
   *  - **--gap** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--breadcrumb-height** - deprecated _(default: undefined)_
   * - **--item-text-size** - deprecated _(default: undefined)_
   * - **--item-color** - deprecated _(default: undefined)_
   * - **--item-active-color** - deprecated _(default: undefined)_
   * - **--item-active-font-weight** - deprecated _(default: undefined)_
   */
  "nve-breadcrumb": Partial<BreadcrumbProps & BaseProps & BaseEvents>;

  /**
   * A button group is a control that enables users to choose between two or more distinct mutually exclusive options.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for `nve-button` or `nve-icon-button`
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   */
  "nve-button-group": Partial<ButtonGroupProps & BaseProps & BaseEvents>;

  /**
   * A button is a widget that enables users to trigger an action or event, such as submitting a form, opening a dialog, canceling an action, or performing a delete operation.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - slot for button text content or icon, icon placement determined by whether `icon` is inserted before or after text content.
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--text-decoration** - undefined _(default: undefined)_
   * - **--text-align** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--text-transform** - undefined _(default: undefined)_
   * - **--line-height** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--min-width** - undefined _(default: undefined)_
   */
  "nve-button": Partial<ButtonProps & BaseProps & BaseEvents>;

  /**
   * A container for content representing a single entity.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - use `<nve-card-header>`,`<nve-card-content>`,`<nve-card-footer>` for card content layout
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--box-shadow** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   */
  "nve-card": Partial<CardProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--border-bottom** - undefined _(default: undefined)_
   * - **--line-height** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   */
  "nve-card-header": Partial<CardHeaderProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - This is a default/unnamed slot for card content content
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   */
  "nve-card-content": Partial<CardContentProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - This is a default/unnamed slot for card footer content
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--border-top** - undefined _(default: undefined)_
   */
  "nve-card-footer": Partial<CardFooterProps & BaseProps & BaseEvents>;

  /**
   * A chat message component displays a text message within a conversation, sent between users or bots
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   * - **prefix** - for avatar/img content
   * - **suffix** - for avatar/img content
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--line-height** - undefined _(default: undefined)_
   * - **--overflow** - undefined _(default: undefined)_
   */
  "nve-chat-message": Partial<ChatMessageProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - Control input elements
   *
   * ### **CSS Properties:**
   *  - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-text-transform** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   */
  "nve-checkbox-group": Partial<CheckboxGroupProps & BaseProps & BaseEvents>;

  /**
   * A checkbox is a control that enables users to choose between two distinct mutually exclusive options (checked or unchecked, on or off) through a single click or tap.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--cursor** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--border-width** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border-color** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--check-color** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-checkbox": Partial<CheckboxProps & BaseProps & BaseEvents>;

  /**
   * A color picker is a control that enables users to choose a color value.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--cursor** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-color": Partial<ColorProps & BaseProps & BaseEvents>;

  /**
   * An editable combobox with autocomplete behavior and selection support.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   * - **selectAll()** - Select all options provided
   *
   * ### **Slots:**
   *  - _default_ - default slot for an input and a datalist/select element
   * - **prefix-icon** - slot for icon to be placed before the input
   * - **footer** - slot for dropdown footer content
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--scroll-height** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-combobox": Partial<ComboboxProps & BaseProps & BaseEvents>;

  /**
   * A copy button is a button that easily enables the copy to clipboard pattern.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default
   * - **icon** - slot for custom icon
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--text-decoration** - undefined _(default: undefined)_
   * - **--text-align** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--text-transform** - undefined _(default: undefined)_
   * - **--line-height** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--min-width** - undefined _(default: undefined)_
   */
  "nve-copy-button": Partial<CopyButtonProps & BaseProps & BaseEvents>;

  /**
   * A date picker is a control that enables users to choose a date value.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--border-bottom** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--max-width** - undefined _(default: undefined)_
   * - **--min-width** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-date": Partial<DateProps & BaseProps & BaseEvents>;

  /**
   * A datetime picker is a control that enables users to choose a datetime value.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--border-bottom** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--max-width** - undefined _(default: undefined)_
   * - **--min-width** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-datetime": Partial<DatetimeProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for the dialog footer
   *
   * ### **CSS Properties:**
   *  - **--border-top** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   */
  "nve-dialog-footer": Partial<DialogFooterProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for the dialog header
   *
   * ### **CSS Properties:**
   *  - **--border-bottom** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   */
  "nve-dialog-header": Partial<DialogHeaderProps & BaseProps & BaseEvents>;

  /**
   * Dialog is a component that appears above main content. A modal dialog is used to display critical information that requires users attention that interrupts user flow. [MDN Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API)
   * ---
   *
   *
   * ### **Events:**
   *  - **beforetoggle** - Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event)
   * - **toggle** - Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event)
   * - **open** - Dispatched when the dialog is opened.
   * - **close** - Dispatched when the dialog is closed.
   *
   * ### **Slots:**
   *  - **default** - content slot
   *
   * ### **CSS Properties:**
   *  - **--border** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--box-shadow** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--max-width** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   *
   * ### **CSS Parts:**
   *  - **close-button** - The inner template reference for the close button of the dialog.
   */
  "nve-dialog": Partial<DialogProps & BaseProps & BaseEvents>;

  /**
   * Divider is a component that separates and distinguishes sections of content or groups of menuitems.
   * ---
   *
   *
   * ### **CSS Properties:**
   *  - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--size** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   */
  "nve-divider": Partial<DividerProps & BaseProps & BaseEvents>;

  /**
   * A visual indicator that communicates a status or notification of an associated component.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default content
   *
   * ### **CSS Properties:**
   *  - **--gap** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   */
  "nve-dot": Partial<DotProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for the drawer content
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   */
  "nve-drawer-content": Partial<DrawerContentProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for the drawer footer
   *
   * ### **CSS Properties:**
   *  - **--border-top** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   */
  "nve-drawer-footer": Partial<DrawerFooterProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for the drawer header
   *
   * ### **CSS Properties:**
   *  - **--border-bottom** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   */
  "nve-drawer-header": Partial<DrawerHeaderProps & BaseProps & BaseEvents>;

  /**
   * Drawer are to display content that is out of context of the rest of the page (notifications, navigation, settings). Alternatively [Panel](./docs/elements/panel/) is inline as its content is coupled or closely related to the content on the page (details, additional actions/options). [MDN Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API)
   * ---
   *
   *
   * ### **Events:**
   *  - **beforetoggle** - Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event)
   * - **toggle** - Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event)
   * - **open** - Dispatched when the drawer is opened.
   * - **close** - Dispatched when the drawer is closed.
   *
   * ### **Slots:**
   *  - **default** - content slot
   *
   * ### **CSS Properties:**
   *  - **--border** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--box-shadow** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--top** - undefined _(default: undefined)_
   * - **--max-width** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   */
  "nve-drawer": Partial<DrawerProps & BaseProps & BaseEvents>;

  /**
   * A Dropdown Group streamlines the management of linked dropdowns and supports nested dropdowns for a more organized and intuitive user experience
   * ---
   *
   *
   * ### **Events:**
   *  - **open** - Dispatched when a dropdown in the group is opened
   * - **close** - Dispatched when a dropdown in the group is closed
   *
   * ### **Slots:**
   *  - _default_ - default slot for dropdown content
   *
   * ### **CSS Properties:**
   *  - **--nve-dropdown-group-spacing** - undefined _(default: undefined)_
   * - **--nve-dropdown-group-transition** - undefined _(default: undefined)_
   */
  "nve-dropdown-group": Partial<DropdownGroupProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for the dropdown footer
   *
   * ### **CSS Properties:**
   *  - **--border-top** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   */
  "nve-dropdown-footer": Partial<DropdownFooterProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for the dropdown header
   *
   * ### **CSS Properties:**
   *  - **--border-bottom** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   */
  "nve-dropdown-header": Partial<DropdownHeaderProps & BaseProps & BaseEvents>;

  /**
   * Generic dropdown element for rendering a variety of different content such as interactive navigation or form controls. [MDN Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API)
   * ---
   *
   *
   * ### **Events:**
   *  - **beforetoggle** - Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event)
   * - **toggle** - Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event)
   * - **open** - Dispatched when the dropdown is opened.
   * - **close** - Dispatched when the dropdown is closed.
   *
   * ### **Slots:**
   *  - _default_ - default slot for dropdown content
   *
   * ### **CSS Properties:**
   *  - **--border** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--box-shadow** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--min-width** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   */
  "nve-dropdown": Partial<DropdownProps & BaseProps & BaseEvents>;

  /**
   * A dropzone form control that enables users to drag anddrop files onto it.
   * ---
   *
   *
   * ### **Events:**
   *  - **change** - emits when the value has changed (files located in event.target)
   *
   * ### **Slots:**
   *  - **icon** - default slot for icon
   * - **content** - default slot for content
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--border-color** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   */
  "nve-dropzone": Partial<DropzoneProps & BaseProps & BaseEvents>;

  /**
   * A file picker is a control that enables users to choose a file value.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--text-decoration** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-file": Partial<FileProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - Control input elements
   *
   * ### **CSS Properties:**
   *  - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-text-transform** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   */
  "nve-control-group": Partial<ControlGroupProps & BaseProps & BaseEvents>;

  /**
   * Defining a Validity State on a control-message will allow messages to be shown conditionally based on the current HTML5 validity state.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   *
   * ### **CSS Properties:**
   *  - **--color** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   */
  "nve-control-message": Partial<ControlMessageProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--cursor** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-control": Partial<ControlProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   * - **--min-width** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--border-left** - undefined _(default: undefined)_
   * - **--border-right** - undefined _(default: undefined)_
   * - **--justify-content** - undefined _(default: undefined)_
   */
  "nve-grid-cell": Partial<GridCellProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Events:**
   *  - **nve-grid-column-resize**
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   * - **actions** - slot for column actions
   *
   * ### **CSS Properties:**
   *  - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--min-width** - undefined _(default: undefined)_
   * - **--justify-content** - undefined _(default: undefined)_
   * - **--border-left** - undefined _(default: undefined)_
   * - **--border-right** - undefined _(default: undefined)_
   */
  "nve-grid-column": Partial<GridColumnProps & BaseProps & BaseEvents>;

  /**
   * Grid footer can be used to display contextual information or additonal user actions such as pagination.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   */
  "nve-grid-footer": Partial<GridFooterProps & BaseProps & BaseEvents>;

  /**
   * A grid is a container enabling users to navigate information or interactive elements it contains using directional navigation keys. As a generic container with flexible keyboard navigation, it can serve a wide variety of needs from a simple use of grouping collections of checkboxes and navigation links to as complex as creating a full-featured spreadsheet. - ARIA Authoring Practices Guide
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   * - **footer** - slot for grid-footer or toolbar
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--box-shadow** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--row-height** - undefined _(default: undefined)_
   * - **--scroll-height** - undefined _(default: undefined)_
   */
  "nve-grid": Partial<GridProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for `nve-grid-column`
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--border-bottom** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   */
  "nve-grid-header": Partial<GridHeaderProps & BaseProps & BaseEvents>;

  /**
   * Placeholder can be used to display a message when data is being loaded for the grid or empty states for datasets.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   *
   * ### **CSS Properties:**
   *  - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   */
  "nve-grid-placeholder": Partial<GridPlaceholderProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for `nve-grid-cell`
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--border-bottom** - undefined _(default: undefined)_
   */
  "nve-grid-row": Partial<GridRowProps & BaseProps & BaseEvents>;

  /**
   * An icon button is a button that displays only an icon without a visual label.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for custom icons
   *
   * ### **CSS Properties:**
   *  - **--border-radius** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--line-height** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--text-decoration** - undefined _(default: undefined)_
   * - **--text-align** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--text-transform** - undefined _(default: undefined)_
   * - **--min-width** - undefined _(default: undefined)_
   */
  "nve-icon-button": Partial<IconButtonProps & BaseProps & BaseEvents>;

  /**
   * An icon is a graphic symbol designed to visually indicate the purpose of an interface element.
   * ---
   *
   *
   * ### **CSS Properties:**
   *  - **--color** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   */
  "nve-icon": Partial<IconProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - Control input elements
   *
   * ### **CSS Properties:**
   *  - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-text-transform** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   */
  "nve-input-group": Partial<InputGroupProps & BaseProps & BaseEvents>;

  /**
   * An input is a control that enables users to enter text.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-input": Partial<InputProps & BaseProps & BaseEvents>;

  /**
   * @deprecated use `nve-monaco-input` instead
   *
   * The JSON Viewer is a custom element that renders JSON data in a easy to read format. This can be used for prototyping and quickly displaying and debugging data. The JSON View is not a substitute for treeview patterns.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for json
   */
  "nve-json-viewer": Partial<JSONViewerProps & BaseProps & BaseEvents>;

  /**
   * A visual indicator for a brand or application.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   */
  "nve-logo": Partial<LogoProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   * - **suffix** - slot for suffix icon
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border-background** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   * - **--line-height** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--opacity** - undefined _(default: undefined)_
   * - **--text-transform** - undefined _(default: undefined)_
   */
  "nve-menu-item": Partial<MenuItemProps & BaseProps & BaseEvents>;

  /**
   * A menu is a widget that offers a list of choices to the user, such as a set of actions or functions. Menu widgets behave like native operating system menus, such as the menus that pull down from the menubars commonly found at the top of many desktop application windows. A menu is usually opened, or made visible, by activating a menu button, choosing an item in a menu that opens a sub menu, or by invoking a command, such as Shift + F10 in Windows, that opens a context specific menu. - ARIA Authoring Practices Guide
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for `nve-menu-item`
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--max-width** - undefined _(default: undefined)_
   * - **--min-width** - undefined _(default: undefined)_
   * - **--max-height** - undefined _(default: undefined)_
   */
  "nve-menu": Partial<MenuProps & BaseProps & BaseEvents>;

  /**
   * A month picker is a control that enables users to choose a month value.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-month": Partial<MonthProps & BaseProps & BaseEvents>;

  /**
   * Displays real time updates without interrupting the user's workflow to communicate an important message or status.
   * ---
   *
   *
   * ### **Slots:**
   *  - **default** - slot for `nve-notification`
   *
   * ### **CSS Properties:**
   *  - **--box-shadow** - undefined _(default: undefined)_
   */
  "nve-notification-group": Partial<NotificationGroupProps & BaseProps & BaseEvents>;

  /**
   * Displays real time updates without interrupting the user's workflow to communicate an important message or status. [MDN Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API)
   * ---
   *
   *
   * ### **Events:**
   *  - **close** - Dispatched when the notification is closed.
   * - **beforetoggle** - Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event)
   * - **toggle** - Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event)
   * - **open** - Dispatched when the notification is opened.
   *
   * ### **Slots:**
   *  - **default** - content slot
   *
   * ### **CSS Properties:**
   *  - **--border-radius** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--box-shadow** - undefined _(default: undefined)_
   * - **--min-width** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--max-width** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   */
  "nve-notification": Partial<NotificationProps & BaseProps & BaseEvents>;

  /**
   * An element that appears across the top of all pages containing the application name and primary navigation.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - undefined
   * - **prefix** - undefined
   * - **suffix** - undefined
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--border-bottom** - undefined _(default: undefined)_
   */
  "nve-page-header": Partial<PageHeaderProps & BaseProps & BaseEvents>;

  /**
   * Page Loader is a full-screen version of the `progress-ring` component, for use when the page should remain unusable as the loader is displayed.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   *
   * ### **CSS Properties:**
   *  - **--gap** - undefined _(default: undefined)_
   */
  "nve-page-loader": Partial<PageLoaderProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for the page-panel content
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   */
  "nve-page-panel-content": Partial<PagePanelContentProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for the page-panel footer
   *
   * ### **CSS Properties:**
   *  - **--border-top** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   */
  "nve-page-panel-footer": Partial<PagePanelFooterProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for the page panel header
   *
   * ### **CSS Properties:**
   *  - **--border-bottom** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   */
  "nve-page-panel-header": Partial<PagePanelHeaderProps & BaseProps & BaseEvents>;

  /**
   * Child panel for embeded panels within the page component. Typically used for left/right/bottom page slot positions.
   * ---
   *
   *
   * ### **Events:**
   *  - **open**
   * - **close**
   *
   * ### **Slots:**
   *  - **default** - content slot
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--max-width** - undefined _(default: undefined)_
   * - **--max-height** - undefined _(default: undefined)_
   */
  "nve-page-panel": Partial<PagePanelProps & BaseProps & BaseEvents>;

  /**
   * Provide a consistent page structure across the applications, ensuring a seamless user experience.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - The central content area of the page, where the primary focus of the user's attention should be.
   * - **header** - The topmost section of the page, typically containing navigation, branding, or other global elements.
   * - **subheader** - A secondary section below the header, often used for breadcrumbs, filters, or other contextual information.
   * - **left-aside** - A narrow section on the left side of the page, commonly used for navigation, filters, or other secondary content.
   * - **left** - The main content area on the left side of the page, typically containing primary navigation or features.
   * - **bottom** - A section for additional tooling outputs such as console outputs.
   * - **right** - The main content area on the right side of the page, typically containing secondary navigation or features.
   * - **right-aside** - A narrow section on the right side of the page, commonly used for navigation, filters, or other secondary content.
   * - **subfooter** - A secondary section below the main content area, often used for additional information or calls to action.
   * - **footer** - The bottommost section of the page, typically containing global elements, such as copyright information.
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   */
  "nve-page": Partial<PageProps & BaseProps & BaseEvents>;

  /**
   * Pagination is a control that enables users to navigate through pages of content.
   * ---
   *
   *
   * ### **Events:**
   *  - **step-change**
   * - **last-page** - emits when the last page is active
   * - **first-page** - emits when the first page is active
   * - **input** - emits when the value (page) has changed
   * - **change** - emits when the value (page) has changed
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   * - **suffix-label** - slot for overriding the "n of total" label when total is an approximation
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   */
  "nve-pagination": Partial<PaginationProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - **title** - Title Text
   * - **subtitle** - Subtitle Text
   * - **action-icon** - Extra Action Button
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--border-bottom** - undefined _(default: undefined)_
   */
  "nve-panel-header": Partial<PanelHeaderProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - This is a default/unnamed slot for panel content content
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   */
  "nve-panel-content": Partial<PanelContentProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - This is a default/unnamed slot for panel footer content
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--border-top** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   */
  "nve-panel-footer": Partial<PanelFooterProps & BaseProps & BaseEvents>;

  /**
   * Panel is inline container for content that is coupled to the content on the page (details, additional actions/options). Alternatively [Drawer](./docs/elements/drawer/) is out of context of the rest of the page (notifications, navigations, settings).
   * ---
   *
   *
   * ### **Events:**
   *  - **open** - Dispatched when the panel is opened.
   * - **close** - Dispatched when the panel is closed.
   *
   * ### **Slots:**
   *  - _default_ - This is a default/unnamed slot for panel content
   * - **header** - header element (Use `panel-header` or custom content)
   * - **content** - content element (Use `panel-content` or custom content)
   * - **footer** - footer element (Use `panel-footer` or custom content)
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--box-shadow** - undefined _(default: undefined)_
   */
  "nve-panel": Partial<PanelProps & BaseProps & BaseEvents>;

  /**
   * A password is a control that enables users to enter password text.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-password": Partial<PasswordProps & BaseProps & BaseEvents>;

  /**
   * A preferences input is a widget for controlling apperance. Stylesheets register to the preferences input by including a css-property, see Standard for an example.
   * ---
   *
   *
   * ### **Events:**
   *  - **input** - emits when the value has changed
   * - **change** - emits when the value has changed
   *
   * ### **CSS Properties:**
   *  - **--color** - undefined _(default: undefined)_
   */
  "nve-preferences-input": Partial<PreferencesInputProps & BaseProps & BaseEvents>;

  /**
   * A progress bar is a visual indicator of the status of a running task. Under the hood the native HTML `progress` element is used to achieve proper a11y concerns.
   * ---
   *
   *
   * ### **CSS Properties:**
   *  - **--height** - undefined _(default: undefined)_
   * - **--opacity** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   */
  "nve-progress-bar": Partial<ProgressBarProps & BaseProps & BaseEvents>;

  /**
   * The `progress-ring` component is used to indicate the status of a pending task. It also serves the basis of the page loading element.
   * ---
   *
   *
   * ### **Slots:**
   *  - **status-icon** - undefined
   *
   * ### **CSS Properties:**
   *  - **--background-color** - undefined _(default: undefined)_
   * - **--ring-color** - undefined _(default: undefined)_
   * - **--ring-background-opacity** - undefined _(default: undefined)_
   * - **--ring-width** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--animation-duration** - undefined _(default: undefined)_
   */
  "nve-progress-ring": Partial<ProgressRingProps & BaseProps & BaseEvents>;

  /**
   * A filter chip is a control that enables users to select multiple options from a set of choices.
   * ---
   *
   *
   * ### **Events:**
   *  - **close** - Dispatched when the filter chip is closed.
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   *
   * ### **CSS Properties:**
   *  - **--gap** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   */
  "nve-progressive-filter-chip": Partial<ProgressiveFilterChipProps & BaseProps & BaseEvents>;

  /**
   * Pulse component is used for signaling/attention for a particular area of a UI. This is helpful for tutorial/getting started guides for new users.
   * ---
   *
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--animation-duration** - undefined _(default: undefined)_
   */
  "nve-pulse": Partial<PulseProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - Control input elements
   *
   * ### **CSS Properties:**
   *  - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-text-transform** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   */
  "nve-radio-group": Partial<RadioGroupProps & BaseProps & BaseEvents>;

  /**
   * A radio button is a control that enables users to choose one option from a list of mutually exclusive options.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--cursor** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--border-width** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border-color** - undefined _(default: undefined)_
   * - **--radio-color** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-radio": Partial<RadioProps & BaseProps & BaseEvents>;

  /**
   * A range slider is a control that enables users to choose a value from a continuous range of values.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--track-width** - undefined _(default: undefined)_
   * - **--track-height** - undefined _(default: undefined)_
   * - **--track-border-radius** - undefined _(default: undefined)_
   * - **--thumb-width** - undefined _(default: undefined)_
   * - **--thumb-height** - undefined _(default: undefined)_
   * - **--thumb-background** - undefined _(default: undefined)_
   * - **--thumb-border** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   */
  "nve-range": Partial<RangeProps & BaseProps & BaseEvents>;

  /**
   * A resize-handle slider is a control that enables users to resize views or panels vertically or horizontally.
   * ---
   *
   *
   * ### **Events:**
   *  - **toggle** - Dispatched when the resize handle is double clicked.
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--line-width** - undefined _(default: undefined)_
   * - **--target-size** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   */
  "nve-resize-handle": Partial<ResizeHandleProps & BaseProps & BaseEvents>;

  /**
   * A search is a control that enables users to enter text to search.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-search": Partial<SearchProps & BaseProps & BaseEvents>;

  /**
   * A select is a control that enables users to select an option from a list of options.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--border-bottom** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--text-align** - undefined _(default: undefined)_
   * - **--scroll-height** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--max-width** - undefined _(default: undefined)_
   * - **--min-width** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   *
   * ### **CSS Parts:**
   *  - **tag** - undefined
   */
  "nve-select": Partial<SelectProps & BaseProps & BaseEvents>;

  /**
   * A loading placeholder component that displays animated placeholder shapes while content loads.
   * ---
   *
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   */
  "nve-skeleton": Partial<SkeletonProps & BaseProps & BaseEvents>;

  /**
   * A sort button is a control that enables users to sort a list of items in ascending or descending order.
   * ---
   *
   *
   * ### **Events:**
   *  - **sort** - Dispatched when the sort button is clicked, returns the current sort value and the next sort value.
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   *
   * ### **CSS Properties:**
   *  - **--width** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   */
  "nve-sort-button": Partial<SortButtonProps & BaseProps & BaseEvents>;

  /**
   * A star rating component lets users rate something using stars, providing a quick visual representation of feedback
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--star-size** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-star-rating": Partial<StarRatingProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for step text
   * - **status-icon** - custom slotted step icon
   *
   * ### **CSS Properties:**
   *  - **--font-size** - undefined _(default: undefined)_
   * - **--border-top** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--text-transform** - undefined _(default: undefined)_
   */
  "nve-steps-item": Partial<StepsItemProps & BaseProps & BaseEvents>;

  /**
   * Steps enables a multi-step workflow allowing a user to complete a goal in a specific sequence.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for steps-item
   *
   * ### **CSS Properties:**
   *  - **--gap** - undefined _(default: undefined)_
   */
  "nve-steps": Partial<StepsProps & BaseProps & BaseEvents>;

  /**
   * A switch is a control that enables users to switch between two mutually exclusive options (on or off, checked or unchecked) through a single click or tap.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--cursor** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border-width** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--anchor-width** - undefined _(default: undefined)_
   * - **--anchor-height** - undefined _(default: undefined)_
   * - **--anchor-border-radius** - undefined _(default: undefined)_
   * - **--anchor-background** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-switch": Partial<SwitchProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   *
   * ### **CSS Properties:**
   *  - **--font-size** - undefined _(default: undefined)_
   * - **--border-width** - undefined _(default: undefined)_
   * - **--border-height** - undefined _(default: undefined)_
   * - **--border-top** - undefined _(default: undefined)_
   * - **--border-background** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--text-transform** - undefined _(default: undefined)_
   */
  "nve-tabs-item": Partial<TabsItemProps & BaseProps & BaseEvents>;

  /**
   * Tabs provide a selection UX, typically used for swapping content shown on a page, or within a navigation context.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for tab-item
   *
   * ### **CSS Properties:**
   *  - **--gap** - undefined _(default: undefined)_
   * - **--indicator-background** - undefined _(default: undefined)_
   * - **--indicator-border-radius** - undefined _(default: undefined)_
   * - **--indicator-height** - undefined _(default: undefined)_
   */
  "nve-tabs": Partial<TabsProps & BaseProps & BaseEvents>;

  /**
   * A interactive element that represents a category or group of content. Typically used to filter or organize content for one to many relations.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--max-width** - undefined _(default: undefined)_
   */
  "nve-tag": Partial<TagProps & BaseProps & BaseEvents>;

  /**
   * A textarea is a control that enables users to enter and edit text.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-textarea": Partial<TextareaProps & BaseProps & BaseEvents>;

  /**
   * A time picker is a control that enables users to choose a time value.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-time": Partial<TimeProps & BaseProps & BaseEvents>;

  /**
   * A contextual popup that displays a status. Toasts are [triggered](https://w3c.github.io/aria/#tooltip) by clicking, focusing, or tapping an element and cannot have interactive elements within them. [MDN Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API)
   * ---
   *
   *
   * ### **Events:**
   *  - **beforetoggle** - Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event)
   * - **toggle** - Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event)
   * - **open** - Dispatched when the toast is opened.
   * - **close** - Dispatched when the toast is closed.
   *
   * ### **Slots:**
   *  - **default** - content slot
   * - **prefix** - custom status icon slot
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--justify-content** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--font-weight** - undefined _(default: undefined)_
   * - **--box-shadow** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   *
   * ### **CSS Parts:**
   *  - **prefix-icon** - The prefix icon slot
   */
  "nve-toast": Partial<ToastProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for the toggletip footer
   *
   * ### **CSS Properties:**
   *  - **--border-top** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   */
  "nve-toggletip-footer": Partial<ToggletipFooterProps & BaseProps & BaseEvents>;

  /**
   *
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for the toggletip header
   *
   * ### **CSS Properties:**
   *  - **--border-bottom** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   */
  "nve-toggletip-header": Partial<ToggletipHeaderProps & BaseProps & BaseEvents>;

  /**
   * Generic toggletip element for rendering a variety of different interactive content. [MDN Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API)
   * ---
   *
   *
   * ### **Events:**
   *  - **beforetoggle** - Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event)
   * - **toggle** - Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event)
   * - **open** - Dispatched when the toggletip is opened.
   * - **close** - Dispatched when the toggletip is closed.
   *
   * ### **Slots:**
   *  - _default_ - default slot for toggletip content
   *
   * ### **CSS Properties:**
   *  - **--arrow-transform** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--box-shadow** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--min-width** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   */
  "nve-toggletip": Partial<ToggletipProps & BaseProps & BaseEvents>;

  /**
   * A toolbar is a container for grouping a set of controls, such as buttons, icon buttons and combobox search.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - default slot for content
   * - **prefix** - slot for prefix content
   * - **suffix** - slot for suffix content
   *
   * ### **CSS Properties:**
   *  - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--gap** - undefined _(default: undefined)_
   * - **--border-bottom** - undefined _(default: undefined)_
   * - **--box-shadow** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   */
  "nve-toolbar": Partial<ToolbarProps & BaseProps & BaseEvents>;

  /**
   * A contextual popup that displays a plaintext description. Tooltips are [triggered](https://w3c.github.io/aria/#tooltip) by hovering, focusing, or tapping an element and cannot have interactive elements within them. [MDN Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API)
   * ---
   *
   *
   * ### **Events:**
   *  - **beforetoggle** - Dispatched on a popover just before it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event)
   * - **toggle** - Dispatched on a popover element just after it is shown or hidden. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event)
   * - **open** - Dispatched when the tooltip is opened.
   * - **close** - Dispatched when the tooltip is closed.
   *
   * ### **Slots:**
   *  - **default** - content slot
   *
   * ### **CSS Properties:**
   *  - **--border-radius** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--padding** - undefined _(default: undefined)_
   * - **--box-shadow** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--arrow-transform** - undefined _(default: undefined)_
   * - **--width** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   *
   * ### **CSS Parts:**
   *  - **arrow** - undefined
   */
  "nve-tooltip": Partial<TooltipProps & BaseProps & BaseEvents>;

  /**
   * A tree view widget presents a hierarchical list. Any item in the hierarchy may have child items, and items that have children may be expanded or collapsed to show or hide the children.
   * ---
   *
   *
   * ### **Events:**
   *  - **open** - Dispatched when the node is opened.
   * - **close** - Dispatched when the node is closed.
   *
   * ### **Methods:**
   *  - **open()** - opens and sets the expanded state automatically if behaviorExpand is true
   * - **close()** - closes and sets the expanded state automatically if behaviorExpand is true
   *
   * ### **Slots:**
   *  - _default_ - Use default slot for basic text content or nested <nve-tree-node> elements.
   * - **content** - Use for extended long form content containing interactive elements or form inputs.
   *
   * ### **CSS Properties:**
   *  - **--color** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--min-height** - undefined _(default: undefined)_
   * - **--text-wrap** - undefined _(default: undefined)_
   */
  "nve-tree-node": Partial<TreeNodeProps & BaseProps & BaseEvents>;

  /**
   * A tree view widget presents a hierarchical list. Any item in the hierarchy may have child items, and items that have children may be expanded or collapsed to show or hide the children.
   * ---
   *
   *
   * ### **Slots:**
   *  - _default_ - tree nodes
   *
   * ### **CSS Properties:**
   *  - **--max-width** - undefined _(default: undefined)_
   */
  "nve-tree": Partial<TreeProps & BaseProps & BaseEvents>;

  /**
   * A week picker is a control that enables users to choose a week value.
   * ---
   *
   *
   * ### **Events:**
   *  - **reset**
   *
   * ### **Methods:**
   *  - **reset()** - Resets control value to initial attribute value and clears any active validation rules.
   *
   * ### **Slots:**
   *  - _default_ - Control input element
   * - **label** - Label element
   *
   * ### **CSS Properties:**
   *  - **--padding** - undefined _(default: undefined)_
   * - **--font-size** - undefined _(default: undefined)_
   * - **--height** - undefined _(default: undefined)_
   * - **--background** - undefined _(default: undefined)_
   * - **--border-radius** - undefined _(default: undefined)_
   * - **--border** - undefined _(default: undefined)_
   * - **--cursor** - undefined _(default: undefined)_
   * - **--accent-color** - undefined _(default: undefined)_
   * - **--color** - undefined _(default: undefined)_
   * - **--label-color** - undefined _(default: undefined)_
   * - **--label-width** - undefined _(default: undefined)_
   * - **--label-font-weight** - undefined _(default: undefined)_
   * - **--label-font-size** - undefined _(default: undefined)_
   * - **--control-width** - undefined _(default: undefined)_
   * - **--control-height** - undefined _(default: undefined)_
   */
  "nve-week": Partial<WeekProps & BaseProps & BaseEvents>;
};
