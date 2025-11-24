"use client";

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface MathTextProps {
  text: string;
  className?: string;
}

/**
 * MathText component - Renders text with Markdown and LaTeX math expressions
 * 
 * Supports:
 * - Markdown formatting (headings, lists, bold, italic, etc.)
 * - Inline math: $...$
 * - Block math: $$...$$
 * - Line breaks and paragraphs
 * 
 * Example:
 * The formula $E = mc^2$ is famous.
 * 
 * Display mode:
 * $$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$
 */
export function MathText({ text, className = "" }: MathTextProps) {
  if (!text) {
    return <span className={className}></span>;
  }

  return (
    <div className={`${className} prose prose-sm max-w-none`}>
      <ReactMarkdown
        remarkPlugins={[remarkMath, remarkGfm]}
        rehypePlugins={[rehypeKatex]}
        components={{
          // Preserve paragraphs with proper spacing
          p: ({ children }) => <p className="mb-2 last:mb-0 whitespace-pre-wrap">{children}</p>,
          // Style lists
          ul: ({ children }) => <ul className="list-disc list-inside mb-2 ml-4">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside mb-2 ml-4">{children}</ol>,
          li: ({ children }) => <li className="mb-1">{children}</li>,
          // Style headings
          h1: ({ children }) => <h1 className="text-xl font-bold mb-2 mt-4 first:mt-0">{children}</h1>,
          h2: ({ children }) => <h2 className="text-lg font-bold mb-2 mt-3 first:mt-0">{children}</h2>,
          h3: ({ children }) => <h3 className="text-base font-bold mb-2 mt-2 first:mt-0">{children}</h3>,
          // Style code blocks
          code: ({ inline, children }) => 
            inline ? (
              <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono">{children}</code>
            ) : (
              <pre className="bg-gray-100 p-3 rounded overflow-x-auto mb-2 text-sm">
                <code className="font-mono">{children}</code>
              </pre>
            ),
          // Style blockquotes
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-gray-300 pl-4 italic my-2">{children}</blockquote>
          ),
          // Style links
          a: ({ href, children }) => (
            <a href={href} className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
          // Style tables
          table: ({ children }) => (
            <table className="border-collapse border border-gray-300 my-2">{children}</table>
          ),
          th: ({ children }) => (
            <th className="border border-gray-300 px-2 py-1 bg-gray-100 font-semibold">{children}</th>
          ),
          td: ({ children }) => (
            <td className="border border-gray-300 px-2 py-1">{children}</td>
          ),
          // Style horizontal rules
          hr: () => <hr className="my-4 border-gray-300" />,
          // Style strong/bold
          strong: ({ children }) => <strong className="font-bold">{children}</strong>,
          // Style emphasis/italic
          em: ({ children }) => <em className="italic">{children}</em>,
        }}
      >
        {text}
      </ReactMarkdown>
    </div>
  );
}
