/**
 * Completion Engine for Q-IDE
 * Handles ranking, filtering, and formatting of code completions
 * Client-side processing: target <50ms after parse results
 */

interface CompletionSymbol {
  name: string;
  kind: string;
  detail: string;
  documentation?: string;
  line?: number;
  column?: number;
}

interface CompletionItem {
  label: string;
  kind: string;
  detail: string;
  documentation?: string;
  insertText: string;
  sortText: string;
  filterText: string;
  score: number;
}

interface CompletionContext {
  symbols: CompletionSymbol[];
  prefix: string;
  line: number;
  column: number;
  language: string;
}

/**
 * Completion Engine
 * Ranks and filters completions with performance optimization
 */
export class CompletionEngine {
  private readonly maxCompletions = 50;
  private readonly scoreThreshold = 0.1; // Minimum score to include
  private recentlyUsed = new Set<string>();
  private typedPrefixes = new Map<string, number>(); // Frequency map

  constructor() {
    // Warm up with common snippets
    this.recordUsage("console");
    this.recordUsage("function");
    this.recordUsage("class");
  }

  /**
   * Generate completions from symbols
   * Handles ranking, filtering, and formatting
   */
  generateCompletions(context: CompletionContext): CompletionItem[] {
    const startTime = performance.now();

    try {
      if (!context.symbols || context.symbols.length === 0) {
        return [];
      }

      // Remove duplicates by name
      const uniqueSymbols = this.deduplicateSymbols(context.symbols);

      // Score and filter
      let scored = uniqueSymbols
        .map((symbol) => ({
          symbol,
          score: this.scoreCompletion(symbol, context.prefix, context.language),
        }))
        .filter(({ score }) => score >= this.scoreThreshold);

      // Sort by score, then by usage frequency
      scored.sort((a, b) => {
        if (b.score !== a.score) {
          return b.score - a.score;
        }

        const aFreq = this.typedPrefixes.get(a.symbol.name) || 0;
        const bFreq = this.typedPrefixes.get(b.symbol.name) || 0;
        return bFreq - aFreq;
      });

      // Convert to completion items
      const completions = scored
        .slice(0, this.maxCompletions)
        .map(({ symbol }) => this.symbolToCompletionItem(symbol, context.prefix));

      const elapsed = performance.now() - startTime;
      if (elapsed > 50) {
        console.warn(
          `Completion engine exceeded 50ms SLA: ${elapsed.toFixed(1)}ms for ${completions.length} items`
        );
      }

      return completions;
    } catch (error) {
      console.error("Completion engine error:", error);
      return [];
    }
  }

  /**
   * Score a completion symbol against the prefix
   * Factors in: exact match, prefix match, substring match, kind, recency
   */
  private scoreCompletion(symbol: CompletionSymbol, prefix: string, language: string): number {
    let score = 0.5; // Base score

    const name = symbol.name.toLowerCase();
    const lowerPrefix = prefix.toLowerCase();

    if (!lowerPrefix) {
      // No prefix: favor functions and classes
      if (symbol.kind === "Function" || symbol.kind === "Class") {
        score += 0.2;
      }
      // Boost recently used
      if (this.recentlyUsed.has(symbol.name)) {
        score += 0.3;
      }
      return score;
    }

    // Exact match
    if (name === lowerPrefix) {
      return 1.0;
    }

    // Exact match (case-insensitive for start)
    if (name.startsWith(lowerPrefix)) {
      score += 0.4;

      // Bonus for exact case match at start
      if (symbol.name.substring(0, lowerPrefix.length) === prefix) {
        score += 0.1;
      }

      // Bonus for short matches (autocomplete like behavior)
      if (lowerPrefix.length >= 3) {
        score += 0.05;
      }
    }
    // Substring match
    else if (name.includes(lowerPrefix)) {
      score += 0.2;

      // Bonus if match is at word boundary
      if (this.isWordBoundary(name, name.indexOf(lowerPrefix))) {
        score += 0.1;
      }
    }
    // Fuzzy match (first letters match)
    else if (this.fuzzyMatch(name, lowerPrefix)) {
      score += 0.15;
    }
    // Didn't match
    else {
      return 0;
    }

    // Language-specific scoring
    score += this.getLanguageBonus(symbol.kind, language);

    // Recency boost
    if (this.recentlyUsed.has(symbol.name)) {
      score += 0.2;
    }

    // Clamp to [0, 1]
    return Math.min(1.0, score);
  }

  /**
   * Fuzzy match: check if lowercase letters of prefix appear in order in name
   * E.g., "cl" matches "classList"
   */
  private fuzzyMatch(name: string, prefix: string): boolean {
    let nameIdx = 0;
    for (let prefixIdx = 0; prefixIdx < prefix.length; prefixIdx++) {
      const char = prefix[prefixIdx];
      nameIdx = name.indexOf(char, nameIdx);
      if (nameIdx === -1) {
        return false;
      }
      nameIdx++;
    }
    return true;
  }

  /**
   * Check if position is at word boundary (after space or special char)
   */
  private isWordBoundary(str: string, pos: number): boolean {
    if (pos === 0) return true;
    const char = str[pos - 1];
    return /[\s_-]/.test(char);
  }

  /**
   * Get scoring bonus based on symbol kind and language
   */
  private getLanguageBonus(kind: string, language: string): number {
    // Boost common operations in each language
    const kindBonus: { [key: string]: number } = {
      Function: 0.1,
      Class: 0.05,
      Method: 0.08,
      Module: 0.02,
      Type: 0.03,
      Interface: 0.02,
      Variable: 0,
      Property: 0.02,
      Constant: 0.05,
    };

    return kindBonus[kind] || 0;
  }

  /**
   * Convert symbol to completion item with rich formatting
   */
  private symbolToCompletionItem(symbol: CompletionSymbol, prefix: string): CompletionItem {
    const insertText = this.getInsertText(symbol);
    const filterText = symbol.name;

    return {
      label: symbol.name,
      kind: symbol.kind,
      detail: symbol.detail || symbol.name,
      documentation: symbol.documentation,
      insertText,
      sortText: symbol.name, // Sort alphabetically as fallback
      filterText,
      score: this.scoreCompletion(symbol, prefix, ""),
    };
  }

  /**
   * Generate insert text based on symbol kind
   * Adds parentheses for functions, braces for objects, etc.
   */
  private getInsertText(symbol: CompletionSymbol): string {
    const name = symbol.name;

    switch (symbol.kind) {
      case "Function":
      case "Method":
        return `${name}()`;

      case "Class":
        return `${name}`;

      default:
        return name;
    }
  }

  /**
   * Remove duplicate symbols (keep first)
   */
  private deduplicateSymbols(symbols: CompletionSymbol[]): CompletionSymbol[] {
    const seen = new Set<string>();
    return symbols.filter((symbol) => {
      if (seen.has(symbol.name)) {
        return false;
      }
      seen.add(symbol.name);
      return true;
    });
  }

  /**
   * Record that a symbol was used (for boosting in future completions)
   */
  recordUsage(name: string): void {
    this.recentlyUsed.add(name);

    // Track frequency
    const current = this.typedPrefixes.get(name) || 0;
    this.typedPrefixes.set(name, current + 1);

    // Decay old entries (keep recent 100)
    if (this.typedPrefixes.size > 100) {
      const entries = Array.from(this.typedPrefixes.entries())
        .sort(([, a], [, b]) => b - a)
        .slice(0, 100);
      this.typedPrefixes.clear();
      entries.forEach(([k, v]) => this.typedPrefixes.set(k, v));
    }
  }

  /**
   * Get statistics about the engine
   */
  getStats(): { recentlyUsed: number; frequencyTracked: number } {
    return {
      recentlyUsed: this.recentlyUsed.size,
      frequencyTracked: this.typedPrefixes.size,
    };
  }

  /**
   * Clear frequency tracking
   */
  reset(): void {
    this.recentlyUsed.clear();
    this.typedPrefixes.clear();
  }
}

/**
 * Format a completion item for display in Monaco editor
 */
export function formatCompletionForMonaco(item: CompletionItem): any {
  return {
    label: item.label,
    kind: getMonacoCompletionKind(item.kind),
    detail: item.detail,
    documentation: item.documentation ? { value: item.documentation } : undefined,
    insertText: item.insertText,
    sortText: item.sortText,
    filterText: item.filterText,
    range: undefined, // Let Monaco determine range
  };
}

/**
 * Map our kind names to Monaco completion kinds
 */
function getMonacoCompletionKind(kind: string): number {
  const kindMap: { [key: string]: number } = {
    Method: 0,
    Function: 1,
    Constructor: 2,
    Field: 3,
    Variable: 4,
    Class: 5,
    Struct: 6,
    Interface: 7,
    Module: 8,
    Property: 9,
    Event: 10,
    Operator: 11,
    Unit: 12,
    Value: 13,
    Constant: 21,
    Enum: 15,
    EnumMember: 16,
    Keyword: 17,
    Text: 18,
    Color: 19,
    File: 20,
    Reference: 22,
    Folder: 23,
    Snippet: 27,
  };

  return kindMap[kind] ?? 13; // Default to Value
}

/**
 * Mock/demo engine for testing
 */
export function createMockCompletionEngine(): CompletionEngine {
  return new CompletionEngine();
}
