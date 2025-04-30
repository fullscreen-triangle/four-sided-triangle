import React, { useRef, useEffect } from 'react';

/**
 * SyntaxHighlighter - A component that provides syntax highlighting for technical terms
 * while maintaining the functionality of a textarea.
 */
const SyntaxHighlighter = ({ 
  value, 
  onChange, 
  onMouseUp, 
  onKeyUp, 
  placeholder, 
  rows, 
  className, 
  style,
  technicalTerms = []
}) => {
  const textareaRef = useRef(null);
  const highlighterRef = useRef(null);
  
  // Sync scroll position between the textarea and the highlighter
  useEffect(() => {
    const textarea = textareaRef.current;
    const highlighter = highlighterRef.current;
    
    const handleScroll = () => {
      highlighter.scrollTop = textarea.scrollTop;
      highlighter.scrollLeft = textarea.scrollLeft;
    };
    
    textarea.addEventListener('scroll', handleScroll);
    return () => textarea.removeEventListener('scroll', handleScroll);
  }, []);
  
  // Highlight technical terms in the text
  const highlightText = (text) => {
    if (!text) return '';
    
    // Escape special characters for regex
    const escapeRegExp = (string) => {
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
  const formatWithLineBreaks = (text) => {
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
};

export default SyntaxHighlighter;