import React, { useRef, useEffect, forwardRef, ForwardedRef } from 'react';

/**
 * SyntaxHighlighter - A component that provides syntax highlighting for technical terms
 * while maintaining the functionality of a textarea.
 */
interface SyntaxHighlighterProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onMouseUp?: (e: React.MouseEvent<HTMLTextAreaElement>) => void;
  onKeyUp?: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  placeholder?: string;
  rows?: number;
  className?: string;
  style?: React.CSSProperties;
  technicalTerms?: string[];
}

const SyntaxHighlighter = forwardRef((
  { 
    value, 
    onChange, 
    onMouseUp, 
    onKeyUp, 
    placeholder, 
    rows, 
    className, 
    style,
    technicalTerms = []
  }: SyntaxHighlighterProps, 
  ref: ForwardedRef<HTMLTextAreaElement>
) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const highlighterRef = useRef<HTMLDivElement>(null);
  
  // Sync scroll position between the textarea and the highlighter
  useEffect(() => {
    const textarea = textareaRef.current;
    const highlighter = highlighterRef.current;
    
    if (!textarea || !highlighter) return;
    
    const handleScroll = () => {
      highlighter.scrollTop = textarea.scrollTop;
      highlighter.scrollLeft = textarea.scrollLeft;
    };
    
    textarea.addEventListener('scroll', handleScroll);
    return () => textarea.removeEventListener('scroll', handleScroll);
  }, []);
  
  // Sync the forwarded ref with our internal ref
  useEffect(() => {
    if (!ref) return;
    
    if (typeof ref === 'function') {
      ref(textareaRef.current);
    } else {
      ref.current = textareaRef.current;
    }
  }, [ref]);
  
  // Highlight technical terms in the text
  const highlightText = (text: string): string => {
    if (!text) return '';
    
    // Escape special characters for regex
    const escapeRegExp = (string: string): string => {
      return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    };
    
    // Create a regex pattern that matches any of the technical terms
    // Use word boundaries to match whole words only
    const pattern = technicalTerms
      .map(term => `\\b${escapeRegExp(term)}\\b`)
      .join('|');
    
    if (!pattern) return text;
    
    const regex = new RegExp(pattern, 'gi');
    
    // Replace matches with highlighted spans
    return text.replace(regex, match => {
      return `<span class="bg-yellow-200 dark:bg-yellow-800 text-black dark:text-white rounded px-1">${match}</span>`;
    });
  };
  
  // Add line breaks to preserve formatting
  const formatWithLineBreaks = (text: string): string => {
    return text.replace(/\n/g, '<br>');
  };
  
  return (
    <div className="relative">
      {/* The actual textarea (invisible but functional) */}
      <textarea
        ref={textareaRef}
        value={value}
        onChange={onChange}
        onMouseUp={onMouseUp}
        onKeyUp={onKeyUp}
        placeholder={placeholder}
        rows={rows}
        className={`${className} absolute inset-0 w-full h-full resize-none overflow-auto z-10 bg-transparent text-transparent caret-gray-900 dark:caret-white`}
        style={style}
      />
      
      {/* The highlighted display (visible but not interactive) */}
      <div
        ref={highlighterRef}
        className={`${className} w-full h-full resize-none overflow-auto whitespace-pre-wrap`}
        style={{ ...style, pointerEvents: 'none' }}
        dangerouslySetInnerHTML={{ 
          __html: value 
            ? formatWithLineBreaks(highlightText(value)) 
            : `<span class="text-gray-500 dark:text-gray-400">${placeholder || ''}</span>` 
        }}
      />
    </div>
  );
});

SyntaxHighlighter.displayName = 'SyntaxHighlighter';

export default SyntaxHighlighter;