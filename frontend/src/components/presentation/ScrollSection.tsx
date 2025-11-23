import React from 'react';
import { motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

interface ScrollSectionProps {
  children: React.ReactNode;
  isActive: boolean;
  direction: number; // 1 for down (next), -1 for up (prev)
  className?: string;
}

const variants = {
  enter: (direction: number) => ({
    y: direction > 0 ? 1000 : -1000,
    opacity: 0,
    scale: 0.5,
    filter: 'blur(10px)',
    zIndex: 10
  }),
  center: {
    y: 0,
    opacity: 1,
    scale: 1,
    filter: 'blur(0px)',
    zIndex: 1,
    transition: {
      duration: 0.8,
      type: "spring" as const,
      stiffness: 50,
      damping: 20
    }
  },
  exit: (direction: number) => ({
    y: direction < 0 ? 1000 : -1000,
    opacity: 0,
    scale: 0.5, // Shrink as it goes away
    filter: 'blur(10px)',
    zIndex: 0,
    transition: {
      duration: 0.8,
      ease: "easeInOut" as const
    }
  })
};

export const ScrollSection: React.FC<ScrollSectionProps> = ({ children, isActive, direction, className = "" }) => {
  return (
    <motion.div
      className={`absolute inset-0 w-full h-full flex items-center justify-center overflow-hidden ${className}`}
      custom={direction}
      variants={variants}
      initial="enter"
      animate={isActive ? "center" : "exit"}
      exit="exit"
    >
      {children}
    </motion.div>
  );
};

export const ScrollIndicator = () => (
  <motion.div 
    className="absolute bottom-8 left-1/2 transform -translate-x-1/2 text-white/50 flex flex-col items-center gap-2"
    animate={{ y: [0, 10, 0] }}
    transition={{ duration: 2, repeat: Infinity }}
  >
    <span className="text-xs uppercase tracking-widest">Scroll</span>
    <ChevronDown size={20} />
  </motion.div>
);

