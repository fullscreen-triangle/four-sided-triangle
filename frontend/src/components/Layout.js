import React from "react";
import React from 'react';
import { useBreakpoint } from '@/utils/responsive';

const Layout = ({ children, className = "" }) => {
  const breakpoint = useBreakpoint();
  
  // Adjust padding and width based on screen size
  const containerClasses = `w-full h-full inline-block z-0 bg-light dark:bg-dark p-32 
    ${breakpoint.isMobile ? 'px-6 py-12' : ''} 
    ${breakpoint.isTablet ? 'px-12 py-24' : ''} 
    ${className}`;
  
  return (
    <div className={containerClasses}>
      {children}
    </div>
  );
};

export default Layout;
const Layout = ({ children, className = "" }) => {
  return (
    <div
      className={`z-0 inline-block h-full w-full bg-light p-32 dark:bg-dark xl:p-24 lg:p-16 
      md:p-12 sm:p-8 ${className}`}
    >
      {children}
    </div>
  );
};

export default Layout;
