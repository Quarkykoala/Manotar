/**
 * Combines multiple class names into a single string, filtering out falsy values
 * @param classes - Array of class names or conditional class names
 * @returns Combined class names string
 */
export function classNames(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

/**
 * Creates a string of Tailwind CSS classes for focus styles
 * @returns Focus ring classes for accessibility
 */
export const focusRingClasses = 'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500';

/**
 * Creates a string of Tailwind CSS classes for transition styles
 * @returns Transition classes for smooth animations
 */
export const transitionClasses = 'transition-all duration-200 ease-in-out';

/**
 * Creates accessibility-focused button base classes
 * @returns Base button classes with proper styling and focus states
 */
export const buttonBaseClasses = classNames(
  'inline-flex items-center justify-center px-4 py-2 border rounded-md',
  'font-medium focus:outline-none focus:ring-2 focus:ring-offset-2',
  'disabled:opacity-50 disabled:cursor-not-allowed',
  transitionClasses
); 