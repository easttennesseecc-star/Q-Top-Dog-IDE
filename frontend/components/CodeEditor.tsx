/**
 * Monaco Editor Component with Q-IDE IntelliSense Integration
 * Connects frontend parser, completion engine, and backend API
 */

import React, { useRef, useEffect, useState, useCallback } from "react";
import { CompletionEngine, formatCompletionForMonaco } from "../services/completion-engine";

interface EditorProps {
  language: "typescript" | "python" | "javascript";
  initialCode?: string;
  onChange?: (code: string) => void;
  onCompletionsRequested?: (prefix: string) => void;
}

interface ParseWorkerMessage {
  type: "parse" | "error";
  code?: string;
  language?: string;
  symbols?: any[];
}

export const CodeEditor: React.FC<EditorProps> = ({
  language = "typescript",
  initialCode = "",
  onChange,
  onCompletionsRequested,
}) => {
  const editorRef = useRef<any>(null); // Monaco editor instance
  const containerRef = useRef<HTMLDivElement>(null);
  const workerRef = useRef<Worker | null>(null);
  const completionEngineRef = useRef<CompletionEngine>(new CompletionEngine());
  const parseDebounceRef = useRef<NodeJS.Timeout | null>(null);
  const lastParsedCodeRef = useRef<string>("");
  const monacoRef = useRef<any>(null); // Monaco module reference
  const [status, setStatus] = useState<"idle" | "parsing" | "ready">("idle");
  const [parseSymbols, setParseSymbols] = useState<any[]>([]);

  // Initialize Monaco Editor
  useEffect(() => {
    if (!containerRef.current || editorRef.current) return;

    const initMonaco = async () => {
      try {
        // Dynamically import Monaco
        const Monaco = await import("monaco-editor");
        monacoRef.current = Monaco;

        const editor = Monaco.editor.create(containerRef.current!, {
          value: initialCode,
          language: language,
          theme: "vs-dark",
          automaticLayout: true,
          fontSize: 14,
          lineNumbers: "on",
          scrollBeyondLastLine: false,
          wordWrap: "on",
          minimap: { enabled: true },
          formatOnPaste: true,
          formatOnType: true,
          suggestOnTriggerCharacters: true,
        });

        editorRef.current = editor;

        // Override IntelliSense
        setupIntelliSense(editor, Monaco);
      } catch (err) {
        console.error("Failed to load Monaco:", err);
      }
    };

    initMonaco();

    return () => {
      if (editorRef.current) {
        editorRef.current.dispose();
        editorRef.current = null;
      }
    };
  }, [language, initialCode]);

  // Initialize Web Worker for parsing
  useEffect(() => {
    if (typeof Worker === "undefined") {
      console.warn("Web Workers not supported");
      return;
    }

    try {
      workerRef.current = new Worker(
        new URL("../services/workers/code-parser.worker.ts", import.meta.url),
        { type: "module" }
      );

      workerRef.current.onmessage = (event) => {
        const { id, success, result, error } = event.data;

        if (success && result) {
          setParseSymbols(result.symbols || []);
          setStatus("ready");
          console.log(`[CompletionEngine] Parsed ${result.symbols?.length || 0} symbols in ${result.parseTime || 0}ms`);
        } else if (error) {
          console.error("[Worker Error]", error);
          setStatus("idle");
        }
      };

      console.log("[Editor] Web Worker initialized");
    } catch (err) {
      console.error("[Editor] Failed to initialize worker:", err);
    }

    return () => {
      if (workerRef.current) {
        workerRef.current.terminate();
      }
    };
  }, []);

  // Setup IntelliSense provider
  const setupIntelliSense = useCallback(
    (editor: any, Monaco: any) => {
      const completionProvider = {
        provideCompletionItems: async (model: any, position: any, context: any, token: any) => {
          const startTime = performance.now();
          const line = model.getLineContent(position.lineNumber);
          const textBeforeCursor = line.substring(0, position.column - 1);

          // Extract prefix for completion
          const match = textBeforeCursor.match(/\w*$/);
          const prefix = match ? match[0] : "";

          // Call backend for fresh symbols if needed
          try {
            const backendSymbols = await fetchBackendCompletions(model.getValue(), position, language);

            // Merge with parsed symbols
            const allSymbols = [...parseSymbols, ...backendSymbols];

            // Generate completions using engine
            const completions = completionEngineRef.current.generateCompletions({
              symbols: allSymbols,
              prefix,
              line: position.lineNumber,
              column: position.column,
              language,
            });

            const elapsed = performance.now() - startTime;
            if (elapsed > 100) {
              console.warn(`[Completions] SLA exceeded: ${elapsed.toFixed(1)}ms for ${completions.length} items`);
            }

            if (onCompletionsRequested) {
              onCompletionsRequested(prefix);
            }

            return {
              suggestions: completions.map(formatCompletionForMonaco),
              incomplete: completions.length >= 50,
            };
          } catch (err) {
            console.error("[IntelliSense] Error generating completions:", err);
            return { suggestions: [] };
          }
        },

        resolveCompletionItem: async (item: any, token: any) => {
          return item;
        },
      };

      const hoverProvider = {
        provideHover: async (model: any, position: any, token: any) => {
          try {
            const word = model.getWordAtPosition(position);
            if (!word) return null;

            const hover = await fetchBackendHover(word.word, language);
            if (hover) {
              return {
                contents: [{ value: hover.type }],
                range: new Monaco.Range(
                  position.lineNumber,
                  word.startColumn,
                  position.lineNumber,
                  word.endColumn
                ),
              };
            }
          } catch (err) {
            console.error("[Hover] Error:", err);
          }
          return null;
        },
      };

      // Register providers
      Monaco.languages.registerCompletionItemProvider(language, completionProvider);
      Monaco.languages.registerHoverProvider(language, hoverProvider);

      console.log(`[IntelliSense] Registered providers for ${language}`);
    },
    [language, parseSymbols, onCompletionsRequested]
  );

  // Handle code changes
  const handleCodeChange = useCallback(() => {
    if (!editorRef.current) return;

    const code = editorRef.current.getValue();

    if (onChange) {
      onChange(code);
    }

    // Debounce parsing
    if (parseDebounceRef.current) {
      clearTimeout(parseDebounceRef.current);
    }

    setStatus("parsing");

    parseDebounceRef.current = setTimeout(() => {
      if (workerRef.current && code !== lastParsedCodeRef.current) {
        workerRef.current.postMessage({
          action: "parse",
          code,
          language,
        });
        lastParsedCodeRef.current = code;
        completionEngineRef.current.recordUsage(language);
      }
    }, 300); // 300ms debounce
  }, [language, onChange]);

  // Setup editor change listener
  useEffect(() => {
    if (!editorRef.current) return;

    const disposable = editorRef.current.onDidChangeModelContent(handleCodeChange);

    return () => {
      disposable.dispose();
    };
  }, [handleCodeChange]);

  // Trigger initial parse
  useEffect(() => {
    if (editorRef.current && workerRef.current) {
      const code = editorRef.current.getValue();
      if (code && code !== lastParsedCodeRef.current) {
        workerRef.current.postMessage({
          action: "parse",
          code,
          language,
        });
        lastParsedCodeRef.current = code;
      }
    }
  }, [language]);

  return (
    <div className="flex flex-col h-full w-full bg-gray-900">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <div className="text-sm font-medium text-gray-200">{language}</div>
          <div className={`w-2 h-2 rounded-full ${getStatusColor(status)}`} />
          <div className="text-xs text-gray-400">{status}</div>
        </div>
        <div className="text-xs text-gray-400">
          {parseSymbols.length} symbols • <span>{completionEngineRef.current.getStats().frequencyTracked}</span> tracked
        </div>
      </div>

      <div
        ref={containerRef}
        className="flex-1 overflow-hidden"
        style={{ height: "calc(100% - 40px)" }}
      />
    </div>
  );
};

/**
 * Fetch completions from backend API
 */
async function fetchBackendCompletions(
  code: string,
  position: any,
  language: string
): Promise<any[]> {
  try {
    const response = await fetch("/api/v1/intellisense/completions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code,
        position: { line: position.lineNumber - 1, column: position.column - 1 },
        language,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return data.items || [];
  } catch (err) {
    console.error("[Backend] Completion fetch failed:", err);
    return [];
  }
}

/**
 * Fetch hover information from backend API
 */
async function fetchBackendHover(word: string, language: string): Promise<any> {
  try {
    const response = await fetch("/api/v1/intellisense/hover", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        symbol: word,
        language,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return data.hover;
  } catch (err) {
    console.error("[Backend] Hover fetch failed:", err);
    return null;
  }
}

/**
 * Get color for status indicator
 */
function getStatusColor(status: string): string {
  switch (status) {
    case "parsing":
      return "bg-yellow-400";
    case "ready":
      return "bg-green-400";
    default:
      return "bg-gray-400";
  }
}

export default CodeEditor;
