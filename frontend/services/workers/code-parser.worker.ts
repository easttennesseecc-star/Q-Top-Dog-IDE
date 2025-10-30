/**
 * Web Worker for fast, non-blocking code parsing
 * Runs in background thread to avoid blocking UI
 * Target: Parse in <50ms, extract 100+ symbols
 */

interface ParseResult {
  symbols: Symbol[];
  errors: string[];
  parseTimeMs: number;
  symbolCount: number;
}

interface Symbol {
  name: string;
  kind: string;
  line: number;
  column: number;
  detail: string;
  documentation?: string;
}

interface ParseMessage {
  id: string;
  action: "parse" | "analyze" | "clear";
  code: string;
  language: string;
  filePath?: string;
}

interface ResultMessage {
  id: string;
  success: boolean;
  result?: ParseResult;
  error?: string;
}

// Parser implementation
class CodeParser {
  private cache = new Map<string, ParseResult>();
  private readonly maxCacheSize = 100;

  /**
   * Parse code and extract symbols
   * Robust error handling with performance tracking
   */
  parse(code: string, language: string, filePath: string): ParseResult {
    const startTime = performance.now();

    try {
      if (!code || code.trim().length === 0) {
        return {
          symbols: [],
          errors: [],
          parseTimeMs: 0,
          symbolCount: 0,
        };
      }

      // Check cache
      const cacheKey = `${filePath}:${code.length}`;
      const cached = this.cache.get(cacheKey);
      if (cached) {
        return cached;
      }

      // Parse based on language
      let symbols: Symbol[] = [];
      let errors: string[] = [];

      if (language === "typescript" || language === "javascript") {
        [symbols, errors] = this.parseTypeScript(code);
      } else if (language === "python") {
        [symbols, errors] = this.parsePython(code);
      } else {
        errors.push(`Unsupported language: ${language}`);
      }

      const parseTimeMs = performance.now() - startTime;

      // Validate performance SLA
      if (parseTimeMs > 50) {
        console.warn(`Parse exceeded 50ms SLA: ${parseTimeMs.toFixed(1)}ms`);
      }

      const result: ParseResult = {
        symbols,
        errors,
        parseTimeMs,
        symbolCount: symbols.length,
      };

      // Cache result
      this.cacheResult(cacheKey, result);

      return result;
    } catch (error) {
      const parseTimeMs = performance.now() - startTime;
      return {
        symbols: [],
        errors: [
          `Parse error: ${
            error instanceof Error ? error.message : String(error)
          }`,
        ],
        parseTimeMs,
        symbolCount: 0,
      };
    }
  }

  /**
   * Parse TypeScript/JavaScript code
   * Extracts functions, classes, variables, imports
   */
  private parseTypeScript(code: string): [Symbol[], string[]] {
    const symbols: Symbol[] = [];
    const errors: string[] = [];
    const lines = code.split("\n");

    // Check for matching braces
    const openBraces = (code.match(/{/g) || []).length;
    const closeBraces = (code.match(/}/g) || []).length;
    if (openBraces !== closeBraces) {
      errors.push("Unmatched braces");
    }

    lines.forEach((line, lineNo) => {
      const trimmed = line.trim();

      // Skip empty lines and comments
      if (!trimmed || trimmed.startsWith("//") || trimmed.startsWith("/*")) {
        return;
      }

      // Import statements
      const importMatch = trimmed.match(
        /^import\s+(?:{([^}]+)}|(\w+))\s+from\s+['"]([^'"]+)['"]/
      );
      if (importMatch) {
        const names = importMatch[1] ? importMatch[1].split(",") : [importMatch[2]];
        names.forEach((name) => {
          const cleanName = name.trim();
          if (cleanName) {
            symbols.push({
              name: cleanName,
              kind: "Module",
              line: lineNo,
              column: 0,
              detail: `import ${cleanName}`,
            });
          }
        });
      }

      // Function declarations
      const funcMatch = trimmed.match(
        /^(?:async\s+)?function\s+(\w+)\s*\(/
      );
      if (funcMatch) {
        symbols.push({
          name: funcMatch[1],
          kind: "Function",
          line: lineNo,
          column: 0,
          detail: `function ${funcMatch[1]}(...)`,
        });
      }

      // Arrow functions and function expressions
      const arrowMatch = trimmed.match(/^(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(/);
      if (arrowMatch) {
        symbols.push({
          name: arrowMatch[1],
          kind: "Function",
          line: lineNo,
          column: 0,
          detail: `${arrowMatch[1]} = (...)`,
        });
      }

      // Class declarations
      const classMatch = trimmed.match(/^class\s+(\w+)(?:\s+extends\s+(\w+))?/);
      if (classMatch) {
        symbols.push({
          name: classMatch[1],
          kind: "Class",
          line: lineNo,
          column: 0,
          detail: `class ${classMatch[1]}`,
        });
      }

      // Variable declarations
      const varMatch = trimmed.match(
        /^(?:const|let|var)\s+(\w+)\s*=/
      );
      if (varMatch && !arrowMatch) {
        symbols.push({
          name: varMatch[1],
          kind: "Variable",
          line: lineNo,
          column: 0,
          detail: varMatch[1],
        });
      }

      // Interface/Type declarations
      const interfaceMatch = trimmed.match(
        /^(?:interface|type)\s+(\w+)/
      );
      if (interfaceMatch) {
        symbols.push({
          name: interfaceMatch[1],
          kind: "Interface",
          line: lineNo,
          column: 0,
          detail: `${interfaceMatch[0].split(/\s+/)[0]} ${interfaceMatch[1]}`,
        });
      }
    });

    return [symbols, errors];
  }

  /**
   * Parse Python code
   * Extracts functions, classes, imports, variables
   */
  private parsePython(code: string): [Symbol[], string[]] {
    const symbols: Symbol[] = [];
    const errors: string[] = [];
    const lines = code.split("\n");

    // Check for syntax issues
    const openParens = (code.match(/\(/g) || []).length;
    const closeParens = (code.match(/\)/g) || []).length;
    if (openParens !== closeParens) {
      errors.push("Unmatched parentheses");
    }

    lines.forEach((line, lineNo) => {
      const trimmed = line.trim();

      // Skip empty lines and comments
      if (!trimmed || trimmed.startsWith("#")) {
        return;
      }

      // Import statements
      if (trimmed.startsWith("import ")) {
        const importMatch = trimmed.match(/^import\s+(.+?)(?:\s+as\s+(\w+))?$/);
        if (importMatch) {
          symbols.push({
            name: importMatch[2] || importMatch[1],
            kind: "Module",
            line: lineNo,
            column: 0,
            detail: `import ${importMatch[1]}`,
          });
        }
      }

      // From imports
      if (trimmed.startsWith("from ")) {
        const fromMatch = trimmed.match(
          /^from\s+(.+?)\s+import\s+(.+)$/
        );
        if (fromMatch) {
          const imports = fromMatch[2].split(",");
          imports.forEach((imp) => {
            const cleanImp = imp.trim();
            const name = cleanImp.split(" as ")[1] || cleanImp.split(" as ")[0];
            symbols.push({
              name: name.trim(),
              kind: "Variable",
              line: lineNo,
              column: 0,
              detail: name.trim(),
            });
          });
        }
      }

      // Function definitions
      const funcMatch = trimmed.match(/^(?:async\s+)?def\s+(\w+)\s*\(/);
      if (funcMatch) {
        symbols.push({
          name: funcMatch[1],
          kind: "Function",
          line: lineNo,
          column: 0,
          detail: `def ${funcMatch[1]}(...)`,
        });
      }

      // Class definitions
      const classMatch = trimmed.match(/^class\s+(\w+)/);
      if (classMatch) {
        symbols.push({
          name: classMatch[1],
          kind: "Class",
          line: lineNo,
          column: 0,
          detail: `class ${classMatch[1]}`,
        });
      }

      // Variable assignments
      const varMatch = trimmed.match(/^(\w+)\s*=/);
      if (varMatch && !trimmed.includes("def ") && !trimmed.includes("class ")) {
        symbols.push({
          name: varMatch[1],
          kind: "Variable",
          line: lineNo,
          column: 0,
          detail: varMatch[1],
        });
      }
    });

    return [symbols, errors];
  }

  /**
   * Cache parse result with LRU eviction
   */
  private cacheResult(key: string, result: ParseResult): void {
    if (this.cache.size >= this.maxCacheSize) {
      const firstKey = this.cache.keys().next().value;
      if (firstKey) {
        this.cache.delete(firstKey);
      }
    }
    this.cache.set(key, result);
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; maxSize: number } {
    return {
      size: this.cache.size,
      maxSize: this.maxCacheSize,
    };
  }
}

// Global parser instance
const parser = new CodeParser();

/**
 * Message handler for worker
 * Listens for parse requests and sends results back to main thread
 */
self.onmessage = async (event: MessageEvent<ParseMessage>) => {
  const { id, action, code, language, filePath } = event.data;

  let result: ResultMessage;

  try {
    switch (action) {
      case "parse":
        const parseResult = parser.parse(code, language, filePath || "");
        result = {
          id,
          success: true,
          result: parseResult,
        };
        break;

      case "clear":
        parser.clearCache();
        result = {
          id,
          success: true,
          result: {
            symbols: [],
            errors: [],
            parseTimeMs: 0,
            symbolCount: 0,
          },
        };
        break;

      case "analyze":
        const analyzeResult = parser.parse(code, language, filePath || "");
        result = {
          id,
          success: true,
          result: analyzeResult,
        };
        break;

      default:
        result = {
          id,
          success: false,
          error: `Unknown action: ${action}`,
        };
    }
  } catch (error) {
    result = {
      id,
      success: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }

  // Send result back to main thread
  self.postMessage(result);
};

// Export for TypeScript
export {};
