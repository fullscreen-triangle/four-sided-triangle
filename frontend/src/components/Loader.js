'use client';
import { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Loader = ({
    progress: externalProgress = null,
    isLoading = true,
    autoComplete = false,
    duration = 5,
    onComplete = () => {},
}) => {
    const [progress, setProgress] = useState(externalProgress !== null ? externalProgress : 0.3);
    const [isEnded, setIsEnded] = useState(false);
    const [isVisible, setIsVisible] = useState(true);
    const animationRef = useRef(null);

    // Initialize with proper starting state
    useEffect(() => {
        if (isLoading) {
            setIsVisible(true);
            setIsEnded(false);
            
            // If no external progress provided, start at 30%
            if (externalProgress === null && autoComplete) {
                setProgress(0.3);
            }
        }
    }, [isLoading, externalProgress, autoComplete]);

    // Handle external progress updates
    useEffect(() => {
        if (externalProgress !== null && !isEnded) {
            setProgress(externalProgress);
            if (externalProgress >= 1) {
                setTimeout(() => setIsEnded(true), 500);
            }
        }
    }, [externalProgress, isEnded]);

    // Auto-completion animation
    useEffect(() => {
        if (autoComplete && isLoading && !isEnded) {
            const startTime = Date.now();

            const animate = () => {
                const elapsed = (Date.now() - startTime) / 1000;
                const newProgress = Math.min(elapsed / duration, 1);
                setProgress(newProgress);

                if (newProgress < 1) {
                    animationRef.current = requestAnimationFrame(animate);
                } else {
                    setTimeout(() => setIsEnded(true), 500);
                }
            };

            animationRef.current = requestAnimationFrame(animate);
            return () => {
                if (animationRef.current) {
                    cancelAnimationFrame(animationRef.current);
                }
            };
        }
    }, [autoComplete, isLoading, isEnded, duration]);

    // Handle completion
    useEffect(() => {
        if (isEnded) {
            const timer = setTimeout(() => {
                setIsVisible(false);
                setTimeout(() => onComplete(), 300);
            }, 1000);
            
            return () => clearTimeout(timer);
        }
    }, [isEnded, onComplete]);

    // Don't render anything if not loading and already ended
    if (!isLoading && isEnded && !isVisible) return null;

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div 
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-20"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                >
                    <div className="absolute top-1/2 w-full h-0.5 overflow-hidden">
                        {/* Main loader bar */}
                        <motion.div
                            className="w-full h-full bg-white relative"
                            initial={{ scaleX: progress > 0.3 ? progress : 0.3 }}
                            animate={{
                                scaleX: isEnded ? 0 : progress,
                            }}
                            exit={{ scaleX: 0 }}
                            transition={{
                                duration: isEnded ? 1.5 : 0.8,
                                ease: isEnded ? "easeInOut" : "easeOut",
                                type: "spring",
                                stiffness: 50,
                                damping: 20
                            }}
                            style={{
                                originX: isEnded ? 1 : 0,
                            }}
                        >
                            {/* Shine effect */}
                            <motion.div
                                className="absolute top-0 left-0 w-20 h-full"
                                animate={{
                                    x: ["-100%", "400%"],
                                    opacity: [0, 1, 0],
                                }}
                                transition={{
                                    duration: 2,
                                    ease: "easeInOut",
                                    repeat: Infinity,
                                    repeatDelay: 0.5,
                                }}
                                style={{
                                    background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)",
                                }}
                            />
                        </motion.div>

                        {/* Pulsing glow effect */}
                        <motion.div
                            className="absolute top-0 left-0 w-full h-full"
                            animate={{
                                opacity: [0.2, 0.4, 0.2],
                            }}
                            transition={{
                                duration: 1.5,
                                ease: "easeInOut",
                                repeat: Infinity,
                            }}
                            style={{
                                background: "white",
                                filter: "blur(4px)",
                                transform: `scaleX(${progress})`,
                                transformOrigin: isEnded ? "right" : "left",
                            }}
                        />
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default Loader;
