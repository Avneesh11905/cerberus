import { motion, AnimatePresence } from 'framer-motion'
import { Check } from 'lucide-react'

const iconVariants = {
  initial: { opacity: 0, scale: 0.3, y: 5 },
  animate: { opacity: 1, scale: 1, y: 0 },
  exit: { opacity: 0, scale: 0.3, y: -5 },
}

interface AnimatedIconSwapProps {
  isActive: boolean
  activeIcon?: React.ElementType
  inactiveIcon: React.ElementType
  className?: string
  activeClassName?: string
}

export function AnimatedIconSwap({
  isActive,
  activeIcon: ActiveIcon = Check,
  inactiveIcon: InactiveIcon,
  className = 'w-4 h-4',
  activeClassName,
}: AnimatedIconSwapProps) {
  return (
    <AnimatePresence mode="wait">
      {isActive ? (
        <motion.div
          key="active"
          variants={iconVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          transition={{
            type: 'spring',
            stiffness: 500,
            damping: 25,
            mass: 0.5,
          }}
          className="inline-flex items-center justify-center"
        >
          <ActiveIcon className={activeClassName || className} />
        </motion.div>
      ) : (
        <motion.div
          key="inactive"
          variants={iconVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          transition={{
            type: 'spring',
            stiffness: 500,
            damping: 25,
            mass: 0.5,
          }}
          className="inline-flex items-center justify-center"
        >
          <InactiveIcon className={className} />
        </motion.div>
      )}
    </AnimatePresence>
  )
}
