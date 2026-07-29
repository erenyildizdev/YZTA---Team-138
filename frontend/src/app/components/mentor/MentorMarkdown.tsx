import ReactMarkdown, {
  defaultUrlTransform,
  type Components,
} from "react-markdown";

const components: Components = {
  p: ({ children }) => (
    <p className="mb-2 whitespace-pre-wrap break-words last:mb-0">{children}</p>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-inherit">{children}</strong>
  ),
  em: ({ children }) => <em className="italic text-inherit">{children}</em>,
  ul: ({ children }) => (
    <ul className="my-2 list-disc space-y-1 pl-5">{children}</ul>
  ),
  ol: ({ children, start }) => (
    <ol start={start} className="my-2 list-decimal space-y-1 pl-5">
      {children}
    </ol>
  ),
  li: ({ children }) => <li className="break-words pl-0.5">{children}</li>,
  code: ({ children }) => (
    <code className="break-all rounded bg-muted px-1 py-0.5 font-mono text-[0.9em] text-inherit">
      {children}
    </code>
  ),
  pre: ({ children }) => (
    <pre className="my-2 max-w-full overflow-x-auto rounded-lg bg-muted p-2 text-xs">
      {children}
    </pre>
  ),
  a: ({ children, href, title }) => {
    if (!href) {
      return <span className="break-all">{children}</span>;
    }

    const isExternal =
      /^(?:https?:)?\/\//i.test(href);

    return (
      <a
        href={href}
        title={title}
        target={isExternal ? "_blank" : undefined}
        rel={isExternal ? "noopener noreferrer" : undefined}
        className="break-all font-medium underline underline-offset-2"
      >
        {children}
      </a>
    );
  },
  img: () => null,
  blockquote: ({ children }) => (
    <blockquote className="my-2 border-l-2 border-border pl-3 text-muted-foreground">
      {children}
    </blockquote>
  ),
  h1: ({ children }) => (
    <h1 className="mb-1 mt-3 text-base font-semibold first:mt-0">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="mb-1 mt-3 text-sm font-semibold first:mt-0">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="mb-1 mt-3 text-sm font-semibold first:mt-0">{children}</h3>
  ),
  h4: ({ children }) => (
    <h4 className="mb-1 mt-3 text-sm font-semibold first:mt-0">{children}</h4>
  ),
  h5: ({ children }) => (
    <h5 className="mb-1 mt-3 text-sm font-semibold first:mt-0">{children}</h5>
  ),
  h6: ({ children }) => (
    <h6 className="mb-1 mt-3 text-sm font-semibold first:mt-0">{children}</h6>
  ),
};

interface MentorMarkdownProps {
  content: string;
}

export function MentorMarkdown({ content }: MentorMarkdownProps) {
  return (
    <div className="min-w-0 max-w-full break-words">
      <ReactMarkdown
        components={components}
        skipHtml
        urlTransform={defaultUrlTransform}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
