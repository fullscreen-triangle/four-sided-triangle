/**
 * Responsive design utilities for adjusting component layouts
 * based on viewport sizes across the application.
 */
import { useState, useEffect } from 'react';

// Breakpoint definitions aligned with TailwindCSS defaults
const breakpoints = {
  sm: 640,   // Small devices like mobile phones
  md: 768,   // Medium devices like tablets
  lg: 1024,  // Large devices like laptops
  xl: 1280,  // Extra large devices like desktops
  '2xl': 1536 // Extra extra large devices
};

/**
 * Custom hook to track viewport width and return the current breakpoint
 * @returns {Object} Current breakpoint information
 */
export const useBreakpoint = () => {
  // Initialize state with undefined to ensure server and client render match
  const [breakpoint, setBreakpoint] = useState({
    isMobile: false,      // sm and below
    isTablet: false,      // md
    isDesktop: false,     // lg and above
    isLargeDesktop: false, // xl and above
    size: undefined       // Current size label
  });

  useEffect(() => {
    // Handler to update state based on window resize
    const handleResize = () => {
      const width = window.innerWidth;
      
      setBreakpoint({
        isMobile: width < breakpoints.md,
        isTablet: width >= breakpoints.md && width < breakpoints.lg,
        isDesktop: width >= breakpoints.lg,
        isLargeDesktop: width >= breakpoints.xl,
        size: width < breakpoints.sm ? 'xs' : 
              width < breakpoints.md ? 'sm' :
              width < breakpoints.lg ? 'md' :
              width < breakpoints.xl ? 'lg' :
              width < breakpoints['2xl'] ? 'xl' : '2xl'
      });
    };

    // Add event listener
    window.addEventListener('resize', handleResize);
    
    // Call handler right away to update initial state
    handleResize();
    
    // Remove event listener on cleanup
    return () => window.removeEventListener('resize', handleResize);
  }, []); // Empty array ensures effect runs only on mount and unmount

  return breakpoint;
};

/**
 * Utility function to conditionally apply classes based on breakpoint
 * @param {Object} options - Object with breakpoint keys and class values
 * @param {string} defaultClasses - Default classes to always apply
 * @returns {string} Combined class string
 */
export const responsiveClasses = (breakpoint, options, defaultClasses = '') => {
  if (!breakpoint || !options) return defaultClasses;

  let classes = defaultClasses;
  
  if (breakpoint.isMobile && options.mobile) {
    classes += ` ${options.mobile}`;
  }
  
  if (breakpoint.isTablet && options.tablet) {
    classes += ` ${options.tablet}`;
  }
  
  if (breakpoint.isDesktop && options.desktop) {
    classes += ` ${options.desktop}`;
  }
  
  if (breakpoint.isLargeDesktop && options.largeDesktop) {
    classes += ` ${options.largeDesktop}`;
  }
  
  return classes.trim();
};
