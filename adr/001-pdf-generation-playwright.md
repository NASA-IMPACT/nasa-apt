# 1. Re-architect PDF generation to use Playwright
- Author: Tarashish ([@sunu](http://github.com/sunu))
- Date: 2023-02-15

## Context and Problem Statement

Current approach to PDF generation converts ATBDs to LaTeX and then to PDF documents using pyLaTeX and latexmk. This approach has several drawbacks:
- It makes styling changes hard to implement
- LaTeX generation for complex documents is complex and error prone
- Bug fixing is difficult, time consuming and feels a lot like whack-a-mole

## Decision Drivers

So we need a better way to generate PDFs that lets us:
- Easily make styling changes
- Iterate quickly on bug fixes
- Minimize the amount of code we need to change to make styling changes

The PDF generation approach needed to support the following features:
- Support for page numbering and page breaks
- Support for table of contents with page numbers
- Rendered text should be selectable (for copy-pasting)
- Support for rendering math equations, images and tables

## Considered Options

Since we already have a solid HTML representation of the ATBD, converting that to PDF seems like a good option.

We considered the following options:
1. Using a headless Chromium through [Playwright](https://playwright.dev/) to convert HTML to PDF in the backend
2. Using a pure Python library like [WeasyPrint](https://weasyprint.org/) to convert HTML to PDF in the backend
3. Using a purely front-end solution to let the user download the PDF

## Decision Outcome

We chose to go ahead with Playwright because it satisfied all our requirements when combined with [Paged.js](https://pagedjs.org/).

### Positive Consequences

- We can easily make styling changes and iterate quickly on bug fixes
- Styling changes can be made in the front-end without having to change any code in the backend

### Negative Consequences

- The development environment becomes more complex to accommodate the new PDF generation approach
- The base Docker image becomes larger because we need to install Chromium

## Pros and Cons of the Options

### Advantages of Playwright:

- It's a tool by Microsoft. Very robust and well-maintained. Allows using webkit, chromium or firefox in headless mode through an easy to use api
- Manages its own headless browser installation
- Supports rendering CSS, JS through webkit
- Natively supports MathML to render math equations

### Downsides of Playwright:

- Browsers haven't implemented target-counter yet. So Playwright doesn't support that either.
  - But we can use an external library like pagedjs to add support for generating table of contents
  - Useful example repo on using pagedjs: https://github.com/ashok-khanna/pdf

### Advantages of WeasyPrint:

- It is a pure Python library. Hence, easy to integrate into our workflow
- it has support for table of content generation through the use of target-counter and it can support rendering Math equations through Katex.

### Downsides of WeasyPrint:

- it has a custom CSS rendering engine which may not keep up with web standards
- it doesn't have a JS engine. So the input needs to be pre-rendered html without any dependency on Javascript
weasyprint is predominantly maintained by a single author. So it may not be as robust as Playwright

## Related issues:
- https://github.com/NASA-IMPACT/nasa-apt/issues/622
- https://github.com/NASA-IMPACT/nasa-apt/issues/634
- https://github.com/NASA-IMPACT/nasa-apt/issues/635

## PR that implements this decision:
- https://github.com/NASA-IMPACT/nasa-apt/pull/638

