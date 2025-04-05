import { useEffect, useCallback, useRef } from 'react';
import { useTheme } from '../contexts/ThemeContext';

interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  description: string;
  action: () => void;
  preventDefault?: boolean;
}

interface UseKeyboardShortcutsOptions {
  enabled?: boolean;
  shortcuts: KeyboardShortcut[];
}

export function useKeyboardShortcuts({
  enabled = true,
  shortcuts,
}: UseKeyboardShortcutsOptions) {
  const { reducedMotion } = useTheme();
  const shortcutsRef = useRef<KeyboardShortcut[]>(shortcuts);

  // Update shortcuts ref when they change
  useEffect(() => {
    shortcutsRef.current = shortcuts;
  }, [shortcuts]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      // Don't trigger shortcuts when typing in input elements
      if (
        event.target instanceof HTMLElement &&
        (event.target.tagName === 'INPUT' ||
          event.target.tagName === 'TEXTAREA' ||
          event.target.isContentEditable)
      ) {
        return;
      }

      const matchingShortcut = shortcutsRef.current.find(
        (shortcut) =>
          shortcut.key.toLowerCase() === event.key.toLowerCase() &&
          !!shortcut.ctrlKey === event.ctrlKey &&
          !!shortcut.shiftKey === event.shiftKey &&
          !!shortcut.altKey === event.altKey
      );

      if (matchingShortcut) {
        if (matchingShortcut.preventDefault !== false) {
          event.preventDefault();
        }
        matchingShortcut.action();

        // Provide audio feedback for screen readers
        const audio = new Audio();
        audio.src = 'data:audio/wav;base64,UklGRjIAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAAABmYWN0BAAAAAAAAABkYXRhAAAAAA==';
        if (!reducedMotion) {
          audio.play().catch(() => {
            // Ignore errors from browsers that block autoplay
          });
        }
      }
    },
    [enabled, reducedMotion]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  // Return a function to get the list of available shortcuts
  const getShortcuts = useCallback(() => {
    return shortcuts.map((shortcut) => ({
      ...shortcut,
      keyCombo: [
        shortcut.ctrlKey && 'Ctrl',
        shortcut.altKey && 'Alt',
        shortcut.shiftKey && 'Shift',
        shortcut.key,
      ]
        .filter(Boolean)
        .join(' + '),
    }));
  }, [shortcuts]);

  return {
    getShortcuts,
  };
}

// Example usage:
/*
function App() {
  const shortcuts: KeyboardShortcut[] = [
    {
      key: '/',
      description: 'Focus search',
      action: () => {
        document.querySelector<HTMLInputElement>('#search')?.focus();
      },
    },
    {
      key: 'Escape',
      description: 'Clear selection',
      action: clearSelection,
    },
    {
      key: 's',
      ctrlKey: true,
      description: 'Save changes',
      action: saveChanges,
    },
  ];

  const { getShortcuts } = useKeyboardShortcuts({ shortcuts });

  // Render keyboard shortcuts help
  return (
    <div>
      <h2>Keyboard Shortcuts</h2>
      <ul>
        {getShortcuts().map((shortcut) => (
          <li key={shortcut.keyCombo}>
            <kbd>{shortcut.keyCombo}</kbd>: {shortcut.description}
          </li>
        ))}
      </ul>
    </div>
  );
}
*/ 