import React from 'react';
import { Dialog } from '@headlessui/react';
import { useTranslation } from '../hooks/useTranslation';
import { useFocusTrap } from '../hooks/useFocusTrap';
import { classNames, buttonBaseClasses } from '../utils/styles';

interface ShortcutGroup {
  title: string;
  shortcuts: {
    keyCombo: string;
    description: string;
  }[];
}

interface KeyboardShortcutsHelpProps {
  isOpen: boolean;
  onClose: () => void;
  shortcuts: ShortcutGroup[];
}

export const KeyboardShortcutsHelp: React.FC<KeyboardShortcutsHelpProps> = ({
  isOpen,
  onClose,
  shortcuts,
}) => {
  const { t } = useTranslation();
  const dialogRef = useFocusTrap<HTMLDivElement>({
    enabled: isOpen,
    onEscape: onClose,
  });

  if (!isOpen) return null;

  return (
    <Dialog
      as="div"
      className="fixed inset-0 z-50 overflow-y-auto"
      onClose={onClose}
      initialFocus={dialogRef}
    >
      <div className="min-h-screen px-4 text-center">
        {/* Background overlay */}
        <Dialog.Overlay className="fixed inset-0 bg-black bg-opacity-30 transition-opacity" />

        {/* Center the modal */}
        <span
          className="inline-block h-screen align-middle"
          aria-hidden="true"
        >
          &#8203;
        </span>

        {/* Modal panel */}
        <div
          ref={dialogRef}
          className="inline-block w-full max-w-2xl p-6 my-8 text-left align-middle bg-white dark:bg-gray-800 rounded-lg shadow-xl transform transition-all"
          role="dialog"
          aria-modal="true"
          aria-labelledby="keyboard-shortcuts-title"
        >
          <div className="flex justify-between items-start">
            <Dialog.Title
              id="keyboard-shortcuts-title"
              className="text-lg font-medium text-gray-900 dark:text-white"
            >
              {t('accessibility.keyboardShortcuts')}
            </Dialog.Title>
            <button
              type="button"
              className={classNames(
                buttonBaseClasses,
                'p-1 hover:bg-gray-100 dark:hover:bg-gray-700'
              )}
              onClick={onClose}
              aria-label={t('accessibility.closeButton')}
            >
              <svg
                className="h-5 w-5 text-gray-400"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div className="mt-4 space-y-6">
            {shortcuts.map((group) => (
              <div key={group.title} className="space-y-4">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {group.title}
                </h3>
                <div className="border dark:border-gray-700 rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                      {group.shortcuts.map((shortcut) => (
                        <tr
                          key={shortcut.keyCombo}
                          className="hover:bg-gray-50 dark:hover:bg-gray-700"
                        >
                          <td className="px-4 py-2 whitespace-nowrap text-sm">
                            <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded-lg dark:text-gray-100 dark:bg-gray-700 dark:border-gray-600">
                              {shortcut.keyCombo}
                            </kbd>
                          </td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                            {shortcut.description}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 text-sm text-gray-500 dark:text-gray-400">
            <p>{t('accessibility.shortcutsNote')}</p>
          </div>
        </div>
      </div>
    </Dialog>
  );
};

// Example usage:
/*
const shortcuts: ShortcutGroup[] = [
  {
    title: 'Navigation',
    shortcuts: [
      { keyCombo: '/', description: 'Focus search' },
      { keyCombo: 'Esc', description: 'Clear selection' },
      { keyCombo: 'Ctrl + K', description: 'Open command palette' },
    ],
  },
  {
    title: 'Actions',
    shortcuts: [
      { keyCombo: 'Ctrl + S', description: 'Save changes' },
      { keyCombo: 'Ctrl + Z', description: 'Undo' },
      { keyCombo: 'Ctrl + Shift + Z', description: 'Redo' },
    ],
  },
];

function App() {
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsHelpOpen(true)}>Show Keyboard Shortcuts</button>
      <KeyboardShortcutsHelp
        isOpen={isHelpOpen}
        onClose={() => setIsHelpOpen(false)}
        shortcuts={shortcuts}
      />
    </>
  );
}
*/