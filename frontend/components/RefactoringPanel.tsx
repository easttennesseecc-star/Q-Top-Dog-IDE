import React, { useState, useCallback, useRef } from 'react';
import { ChevronDown, RefreshCw, FileMove, Copy, Trash2 } from 'lucide-react';

interface RefactoringOption {
  type: string;
  name: string;
  available: boolean;
  symbol?: string;
}

interface RefactoringChange {
  type: string;
  description: string;
  applied: boolean;
}

/**
 * RefactoringPanel - Refactoring operations UI
 */
const RefactoringPanel: React.FC = () => {
  const [activeOperation, setActiveOperation] = useState<string | null>(null);
  const [availableRefactorings, setAvailableRefactorings] = useState<RefactoringOption[]>([]);
  const [extractName, setExtractName] = useState('extracted_function');
  const [renameOld, setRenameOld] = useState('');
  const [renameNew, setRenameNew] = useState('');
  const [moveSymbol, setMoveSymbol] = useState('');
  const [moveTarget, setMoveTarget] = useState('');
  const [changes, setChanges] = useState<RefactoringChange[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(false);

  const currentLine = useRef(1);
  const currentCol = useRef(0);

  /**
   * Fetch available refactorings at cursor position
   */
  const fetchAvailableRefactorings = useCallback(async (source: string, line: number, col: number) => {
    try {
      const response = await fetch('/api/v1/refactor/available', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, line, col }),
      });

      const data = await response.json();
      setAvailableRefactorings(data.refactorings || []);
    } catch (error) {
      console.error('Error fetching refactorings:', error);
    }
  }, []);

  /**
   * Extract function operation
   */
  const handleExtractFunction = useCallback(async (
    source: string,
    name: string,
    startLine: number,
    endLine: number,
    parameters: string[]
  ) => {
    setIsProcessing(true);
    try {
      const response = await fetch('/api/v1/refactor/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source,
          name,
          start_line: startLine,
          end_line: endLine,
          parameters,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setChanges(data.changes.map((change: any) => ({
          type: change.type,
          description: `Extract function '${change.function_name}' (lines ${change.start_line}-${change.end_line})`,
          applied: true,
        })));
        setPreviewOpen(true);
      } else {
        setChanges([{
          type: 'error',
          description: data.error || 'Failed to extract function',
          applied: false,
        }]);
      }
    } catch (error) {
      setChanges([{
        type: 'error',
        description: `Error: ${error}`,
        applied: false,
      }]);
    } finally {
      setIsProcessing(false);
    }
  }, []);

  /**
   * Rename symbol operation
   */
  const handleRenameSymbol = useCallback(async (source: string, oldName: string, newName: string) => {
    setIsProcessing(true);
    try {
      const response = await fetch('/api/v1/refactor/rename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source,
          old_name: oldName,
          new_name: newName,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setChanges([{
          type: 'rename',
          description: `Renamed '${oldName}' to '${newName}' (${data.changes} occurrences)`,
          applied: true,
        }]);
        setPreviewOpen(true);
      } else {
        setChanges([{
          type: 'error',
          description: data.error || 'Failed to rename symbol',
          applied: false,
        }]);
      }
    } catch (error) {
      setChanges([{
        type: 'error',
        description: `Error: ${error}`,
        applied: false,
      }]);
    } finally {
      setIsProcessing(false);
    }
  }, []);

  /**
   * Move to file operation
   */
  const handleMoveToFile = useCallback(async (source: string, symbol: string, target: string) => {
    setIsProcessing(true);
    try {
      const response = await fetch('/api/v1/refactor/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source,
          symbol_name: symbol,
          target_file: target,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setChanges(data.source_file_changes.map((change: any) => ({
          type: change.type,
          description: `Moved '${change.symbol}' to '${change.target_file}'`,
          applied: true,
        })));
        setPreviewOpen(true);
      } else {
        setChanges([{
          type: 'error',
          description: data.error || 'Failed to move to file',
          applied: false,
        }]);
      }
    } catch (error) {
      setChanges([{
        type: 'error',
        description: `Error: ${error}`,
        applied: false,
      }]);
    } finally {
      setIsProcessing(false);
    }
  }, []);

  return (
    <div className="bg-gray-900 text-white p-4 rounded-lg border border-gray-700">
      <div className="flex items-center gap-2 mb-4">
        <RefreshCw size={18} />
        <h3 className="font-semibold">Refactoring</h3>
      </div>

      {/* Available Refactorings */}
      {availableRefactorings.length > 0 && (
        <div className="mb-4 p-3 bg-gray-800 rounded border border-gray-700">
          <p className="text-sm text-gray-400 mb-2">Available at cursor:</p>
          <div className="flex flex-wrap gap-2">
            {availableRefactorings.map((ref) => (
              <button
                key={ref.type}
                onClick={() => setActiveOperation(ref.type)}
                disabled={!ref.available}
                className={`px-3 py-1 rounded text-sm ${
                  ref.available
                    ? 'bg-blue-600 hover:bg-blue-700 cursor-pointer'
                    : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                }`}
              >
                {ref.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Extract Function Panel */}
      {activeOperation === 'extract_function' && (
        <div className="mb-4 p-3 bg-gray-800 rounded border border-gray-700">
          <h4 className="font-semibold mb-3">Extract Function</h4>
          <input
            type="text"
            placeholder="Function name"
            value={extractName}
            onChange={(e) => setExtractName(e.target.value)}
            className="w-full mb-2 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          />
          <input
            type="text"
            placeholder="Start line"
            className="w-full mb-2 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          />
          <input
            type="text"
            placeholder="End line"
            className="w-full mb-2 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          />
          <button
            onClick={() => handleExtractFunction('', extractName, 1, 5, [])}
            disabled={isProcessing}
            className="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-semibold disabled:opacity-50"
          >
            {isProcessing ? 'Processing...' : 'Extract'}
          </button>
        </div>
      )}

      {/* Rename Symbol Panel */}
      {activeOperation === 'rename_symbol' && (
        <div className="mb-4 p-3 bg-gray-800 rounded border border-gray-700">
          <h4 className="font-semibold mb-3">Rename Symbol</h4>
          <input
            type="text"
            placeholder="Current name"
            value={renameOld}
            onChange={(e) => setRenameOld(e.target.value)}
            className="w-full mb-2 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          />
          <input
            type="text"
            placeholder="New name"
            value={renameNew}
            onChange={(e) => setRenameNew(e.target.value)}
            className="w-full mb-2 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          />
          <button
            onClick={() => handleRenameSymbol('', renameOld, renameNew)}
            disabled={isProcessing || !renameOld || !renameNew}
            className="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-semibold disabled:opacity-50"
          >
            {isProcessing ? 'Processing...' : 'Rename'}
          </button>
        </div>
      )}

      {/* Move to File Panel */}
      {activeOperation === 'move_to_file' && (
        <div className="mb-4 p-3 bg-gray-800 rounded border border-gray-700">
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <FileMove size={16} /> Move to File
          </h4>
          <input
            type="text"
            placeholder="Symbol name"
            value={moveSymbol}
            onChange={(e) => setMoveSymbol(e.target.value)}
            className="w-full mb-2 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          />
          <input
            type="text"
            placeholder="Target file (e.g., utils.py)"
            value={moveTarget}
            onChange={(e) => setMoveTarget(e.target.value)}
            className="w-full mb-2 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          />
          <button
            onClick={() => handleMoveToFile('', moveSymbol, moveTarget)}
            disabled={isProcessing || !moveSymbol || !moveTarget}
            className="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-semibold disabled:opacity-50"
          >
            {isProcessing ? 'Processing...' : 'Move'}
          </button>
        </div>
      )}

      {/* Changes Preview */}
      {changes.length > 0 && previewOpen && (
        <div className="p-3 bg-gray-800 rounded border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-semibold text-sm">Changes</h4>
            <button
              onClick={() => setPreviewOpen(false)}
              className="text-gray-400 hover:text-white"
            >
              <ChevronDown size={16} />
            </button>
          </div>
          <div className="space-y-2">
            {changes.map((change, idx) => (
              <div
                key={idx}
                className={`text-sm p-2 rounded ${
                  change.applied
                    ? 'bg-green-900 text-green-100 border border-green-700'
                    : 'bg-red-900 text-red-100 border border-red-700'
                }`}
              >
                <div className="flex items-start gap-2">
                  {change.applied ? (
                    <Copy size={14} className="flex-shrink-0 mt-0.5" />
                  ) : (
                    <Trash2 size={14} className="flex-shrink-0 mt-0.5" />
                  )}
                  <span>{change.description}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info */}
      <div className="text-xs text-gray-400 mt-4 p-2 bg-gray-800 rounded">
        <p>• Extract: Select code range and extract to function</p>
        <p>• Rename: Rename symbol across all references</p>
        <p>• Move: Move function/class to new file</p>
      </div>
    </div>
  );
};

export default RefactoringPanel;
