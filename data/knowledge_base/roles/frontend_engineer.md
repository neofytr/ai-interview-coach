# Frontend Engineer — Interview Guide

## React, JavaScript, and Core Web Technologies

Frontend interviews assess deep understanding of the rendering pipeline, not just API familiarity. Interviewers ask "Explain the React component lifecycle" as a baseline, but the real test comes from follow-ups: "Why might useEffect with an empty dependency array behave differently than componentDidMount?" or "When would you use useRef instead of useState?" Strong candidates explain the mental model — React's reconciliation algorithm, virtual DOM diffing, how state updates are batched — rather than reciting documentation.

Key competencies: closures, event loop and asynchronous JavaScript, prototype chain, ES6+ idioms, TypeScript type safety in props and state, and understanding controlled vs. uncontrolled components. Candidates should demonstrate comfort with state management patterns — knowing when local state suffices vs. when a global solution (Context, Redux, Zustand) is warranted.

Common pitfall: over-engineering state management. Introducing Redux for three components with no shared state is a negative signal. Another is inability to explain re-render behavior — candidates who cannot trace why a component re-renders or how React.memo and useMemo affect performance reveal shallow understanding.

## Accessibility and Semantic HTML

Accessibility is a first-class evaluation criterion at serious engineering organizations. Interviewers ask candidates to build a dropdown menu, modal, or autocomplete and then evaluate whether they use semantic elements, manage focus correctly, handle keyboard navigation, and apply ARIA attributes appropriately. A candidate who builds a clickable div instead of a button, or a custom select that is unreachable via keyboard, demonstrates a gap that matters.

Evaluation criteria: understanding of the accessibility tree, screen reader behavior, WCAG guidelines (especially contrast ratios, focus indicators, and alt text), and the ability to audit existing UI for accessibility issues. Great candidates mention automated tools (axe, Lighthouse) and manual testing with screen readers as part of their development workflow, not as an afterthought.

## Performance Optimization

Interviewers probe performance knowledge through questions like "This page takes 4 seconds to load — how do you investigate and fix it?" Strong candidates describe a systematic approach: measure first (Core Web Vitals, Lighthouse, browser DevTools Performance tab), identify the bottleneck (large bundle, render-blocking resources, excessive re-renders, layout thrashing), then apply targeted fixes.

Key areas: code splitting and lazy loading, image optimization (modern formats, responsive images, lazy loading), critical rendering path, debouncing/throttling expensive handlers, virtualization for long lists, and understanding when server-side rendering or static generation improves perceived performance. Candidates who optimize without measuring first — or who apply micro-optimizations while ignoring a 2MB JavaScript bundle — reveal misplaced priorities.

## Component Design and Architecture

Senior frontend candidates are expected to design component APIs that are reusable, composable, and maintainable. Interviewers present scenarios like "Design a Table component supporting sorting, filtering, pagination, and custom renderers." They evaluate whether the candidate considers the public API (props interface), separation of concerns, composition patterns (render props, compound components, hooks), and scalability as requirements grow. Strong candidates discuss error states, loading states, and empty states as integral parts of the design.
