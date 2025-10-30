/**
 * Unit Tests for Completion Engine
 * Validates ranking, scoring, filtering, and performance
 */

import { CompletionEngine, formatCompletionForMonaco } from "../services/completion-engine";

describe("CompletionEngine", () => {
  let engine: CompletionEngine;

  beforeEach(() => {
    engine = new CompletionEngine();
  });

  describe("Deduplication", () => {
    test("removes duplicate symbols by name", () => {
      const symbols = [
        { name: "foo", kind: "Function", detail: "foo()" },
        { name: "foo", kind: "Function", detail: "foo() duplicate" },
        { name: "bar", kind: "Variable", detail: "bar" },
      ];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "",
        line: 1,
        column: 1,
        language: "typescript",
      });

      const names = completions.map((c) => c.label);
      const fooCount = names.filter((n) => n === "foo").length;
      expect(fooCount).toBe(1);
    });
  });

  describe("Scoring", () => {
    test("exact match gets score 1.0", () => {
      const symbols = [
        { name: "console", kind: "Variable", detail: "console" },
      ];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "console",
        line: 1,
        column: 1,
        language: "typescript",
      });

      expect(completions.length).toBe(1);
      expect(completions[0].score).toBe(1.0);
    });

    test("prefix match scores higher than substring match", () => {
      const symbols = [
        { name: "console", kind: "Variable", detail: "console" },
        { name: "dconsole", kind: "Variable", detail: "dconsole" },
      ];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "con",
        line: 1,
        column: 1,
        language: "typescript",
      });

      // console should rank higher (prefix match)
      const consoleItem = completions.find((c) => c.label === "console");
      const dconsoleItem = completions.find((c) => c.label === "dconsole");

      if (consoleItem && dconsoleItem) {
        expect(consoleItem.score).toBeGreaterThan(dconsoleItem.score);
      }
    });

    test("functions and classes get boosted in scoring", () => {
      const symbols = [
        { name: "myFunc", kind: "Function", detail: "myFunc()" },
        { name: "myVar", kind: "Variable", detail: "myVar" },
      ];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "",
        line: 1,
        column: 1,
        language: "typescript",
      });

      const funcItem = completions.find((c) => c.label === "myFunc");
      const varItem = completions.find((c) => c.label === "myVar");

      if (funcItem && varItem) {
        expect(funcItem.score).toBeGreaterThanOrEqual(varItem.score);
      }
    });

    test("case-sensitive prefix match gets bonus", () => {
      const symbols = [
        { name: "Console", kind: "Class", detail: "Console" },
        { name: "console", kind: "Variable", detail: "console" },
      ];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "Con",
        line: 1,
        column: 1,
        language: "typescript",
      });

      // Capital C match should rank higher
      const capitalItem = completions.find((c) => c.label === "Console");
      const lowerItem = completions.find((c) => c.label === "console");

      if (capitalItem && lowerItem) {
        expect(capitalItem.score).toBeGreaterThanOrEqual(lowerItem.score);
      }
    });
  });

  describe("Fuzzy Matching", () => {
    test("fuzzy matches partial words", () => {
      const symbols = [{ name: "classList", kind: "Property", detail: "classList" }];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "cl",
        line: 1,
        column: 1,
        language: "typescript",
      });

      expect(completions.length).toBeGreaterThan(0);
      expect(completions[0].label).toBe("classList");
    });

    test("fuzzy match scores lower than prefix match", () => {
      const symbols = [
        { name: "classList", kind: "Property", detail: "classList" },
        { name: "class", kind: "Keyword", detail: "class" },
      ];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "cl",
        line: 1,
        column: 1,
        language: "typescript",
      });

      // class is prefix match, classList is fuzzy match
      const classItem = completions.find((c) => c.label === "class");
      const classListItem = completions.find((c) => c.label === "classList");

      if (classItem && classListItem) {
        expect(classItem.score).toBeGreaterThan(classListItem.score);
      }
    });
  });

  describe("Filtering", () => {
    test("removes low-scoring items below threshold", () => {
      const symbols = [
        { name: "z", kind: "Variable", detail: "z" },
        { name: "a", kind: "Variable", detail: "a" },
        { name: "zzzzz", kind: "Variable", detail: "zzzzz" },
      ];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "a",
        line: 1,
        column: 1,
        language: "typescript",
      });

      // Should only find "a", not the z's
      expect(completions.length).toBe(1);
      expect(completions[0].label).toBe("a");
    });

    test("limits results to maxCompletions (50)", () => {
      const symbols = Array.from({ length: 100 }, (_, i) => ({
        name: `var_${i}`,
        kind: "Variable",
        detail: `var_${i}`,
      }));

      const completions = engine.generateCompletions({
        symbols,
        prefix: "var",
        line: 1,
        column: 1,
        language: "typescript",
      });

      expect(completions.length).toBeLessThanOrEqual(50);
    });
  });

  describe("Insert Text Generation", () => {
    test("functions get parentheses", () => {
      const symbols = [{ name: "myFunc", kind: "Function", detail: "myFunc()" }];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "my",
        line: 1,
        column: 1,
        language: "typescript",
      });

      expect(completions[0].insertText).toBe("myFunc()");
    });

    test("methods get parentheses", () => {
      const symbols = [{ name: "toString", kind: "Method", detail: "toString()" }];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "to",
        line: 1,
        column: 1,
        language: "typescript",
      });

      expect(completions[0].insertText).toBe("toString()");
    });

    test("classes don't get parentheses", () => {
      const symbols = [{ name: "MyClass", kind: "Class", detail: "MyClass" }];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "My",
        line: 1,
        column: 1,
        language: "typescript",
      });

      expect(completions[0].insertText).toBe("MyClass");
    });

    test("variables and properties don't get parentheses", () => {
      const symbols = [{ name: "myVar", kind: "Variable", detail: "myVar" }];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "my",
        line: 1,
        column: 1,
        language: "typescript",
      });

      expect(completions[0].insertText).toBe("myVar");
    });
  });

  describe("Usage Tracking", () => {
    test("records symbol usage", () => {
      engine.recordUsage("console");

      const stats = engine.getStats();
      expect(stats.frequencyTracked).toBeGreaterThan(0);
    });

    test("recently used symbols get boosted", () => {
      const symbols = [
        { name: "console", kind: "Variable", detail: "console" },
        { name: "document", kind: "Variable", detail: "document" },
      ];

      // Record console as used
      engine.recordUsage("console");

      const completions = engine.generateCompletions({
        symbols,
        prefix: "",
        line: 1,
        column: 1,
        language: "typescript",
      });

      const consoleItem = completions.find((c) => c.label === "console");
      const docItem = completions.find((c) => c.label === "document");

      if (consoleItem && docItem) {
        expect(consoleItem.score).toBeGreaterThan(docItem.score);
      }
    });

    test("resets usage tracking", () => {
      engine.recordUsage("test");
      engine.reset();

      const stats = engine.getStats();
      expect(stats.frequencyTracked).toBe(0);
    });
  });

  describe("Performance", () => {
    test("generates completions in <50ms for 100 symbols", () => {
      const symbols = Array.from({ length: 100 }, (_, i) => ({
        name: `symbol_${i}`,
        kind: "Variable",
        detail: `symbol_${i}`,
      }));

      const start = performance.now();
      const completions = engine.generateCompletions({
        symbols,
        prefix: "symbol",
        line: 1,
        column: 1,
        language: "typescript",
      });
      const elapsed = performance.now() - start;

      expect(elapsed).toBeLessThan(50);
    });

    test("generates completions in <30ms for 50 symbols", () => {
      const symbols = Array.from({ length: 50 }, (_, i) => ({
        name: `symbol_${i}`,
        kind: "Variable",
        detail: `symbol_${i}`,
      }));

      const start = performance.now();
      const completions = engine.generateCompletions({
        symbols,
        prefix: "sym",
        line: 1,
        column: 1,
        language: "typescript",
      });
      const elapsed = performance.now() - start;

      expect(elapsed).toBeLessThan(30);
    });
  });

  describe("Language-Specific Scoring", () => {
    test("boosts TypeScript specific kinds", () => {
      const symbols = [
        { name: "MyInterface", kind: "Interface", detail: "MyInterface" },
        { name: "myVar", kind: "Variable", detail: "myVar" },
      ];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "",
        line: 1,
        column: 1,
        language: "typescript",
      });

      const interfaceItem = completions.find((c) => c.label === "MyInterface");
      const varItem = completions.find((c) => c.label === "myVar");

      if (interfaceItem && varItem) {
        expect(interfaceItem.score).toBeGreaterThanOrEqual(varItem.score);
      }
    });
  });

  describe("Edge Cases", () => {
    test("handles empty symbol list", () => {
      const completions = engine.generateCompletions({
        symbols: [],
        prefix: "any",
        line: 1,
        column: 1,
        language: "typescript",
      });

      expect(completions.length).toBe(0);
    });

    test("handles empty prefix", () => {
      const symbols = [
        { name: "foo", kind: "Function", detail: "foo()" },
        { name: "bar", kind: "Function", detail: "bar()" },
      ];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "",
        line: 1,
        column: 1,
        language: "typescript",
      });

      expect(completions.length).toBeGreaterThan(0);
    });

    test("handles special characters in prefix", () => {
      const symbols = [
        { name: "my_var", kind: "Variable", detail: "my_var" },
      ];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "my_",
        line: 1,
        column: 1,
        language: "typescript",
      });

      expect(completions.length).toBeGreaterThan(0);
    });

    test("handles very long symbol names", () => {
      const longName = "a".repeat(200);
      const symbols = [{ name: longName, kind: "Variable", detail: longName }];

      const completions = engine.generateCompletions({
        symbols,
        prefix: "aaa",
        line: 1,
        column: 1,
        language: "typescript",
      });

      expect(completions.length).toBeGreaterThan(0);
    });
  });

  describe("Monaco Formatting", () => {
    test("formats completion for Monaco editor", () => {
      const item = {
        label: "console",
        kind: "Variable",
        detail: "console object",
        documentation: "Browser console",
        insertText: "console",
        sortText: "console",
        filterText: "console",
        score: 0.9,
      };

      const formatted = formatCompletionForMonaco(item);

      expect(formatted.label).toBe("console");
      expect(formatted.detail).toBe("console object");
      expect(formatted.documentation).toBeDefined();
      expect(formatted.insertText).toBe("console");
    });

    test("handles missing documentation", () => {
      const item = {
        label: "foo",
        kind: "Function",
        detail: "foo()",
        insertText: "foo()",
        sortText: "foo",
        filterText: "foo",
        score: 0.8,
      };

      const formatted = formatCompletionForMonaco(item);

      expect(formatted.documentation).toBeUndefined();
    });
  });
});

describe("Accuracy Validation", () => {
  let engine: CompletionEngine;

  beforeEach(() => {
    engine = new CompletionEngine();
  });

  test("90% accuracy on TypeScript completions", () => {
    const testCases = [
      {
        prefix: "con",
        expected: ["console", "const", "constructor"],
        symbols: [
          { name: "console", kind: "Variable", detail: "console" },
          { name: "const", kind: "Keyword", detail: "const" },
          { name: "constructor", kind: "Method", detail: "constructor()" },
          { name: "Array", kind: "Class", detail: "Array" },
        ],
      },
      {
        prefix: "arr",
        expected: ["Array"],
        symbols: [
          { name: "Array", kind: "Class", detail: "Array" },
          { name: "arguments", kind: "Variable", detail: "arguments" },
        ],
      },
      {
        prefix: "str",
        expected: ["String", "stringify"],
        symbols: [
          { name: "String", kind: "Class", detail: "String" },
          { name: "stringify", kind: "Method", detail: "stringify()" },
        ],
      },
    ];

    let correctPredictions = 0;

    testCases.forEach(({ prefix, expected, symbols }) => {
      const completions = engine.generateCompletions({
        symbols,
        prefix,
        line: 1,
        column: 1,
        language: "typescript",
      });

      const completionNames = completions.map((c) => c.label);
      const matches = expected.filter((e) =>
        completionNames.some((n) => n.toLowerCase().includes(e.toLowerCase()))
      );

      if (matches.length > 0) {
        correctPredictions++;
      }
    });

    const accuracy = correctPredictions / testCases.length;
    expect(accuracy).toBeGreaterThanOrEqual(0.9);
  });

  test("90% accuracy on Python completions", () => {
    const testCases = [
      {
        prefix: "print",
        expected: ["print"],
        symbols: [
          { name: "print", kind: "Function", detail: "print(...)" },
          { name: "printf", kind: "Function", detail: "printf(...)" },
        ],
      },
      {
        prefix: "len",
        expected: ["len"],
        symbols: [
          { name: "len", kind: "Function", detail: "len(...)" },
          { name: "lend", kind: "Variable", detail: "lend" },
        ],
      },
    ];

    let correctPredictions = 0;

    testCases.forEach(({ prefix, expected, symbols }) => {
      const completions = engine.generateCompletions({
        symbols,
        prefix,
        line: 1,
        column: 1,
        language: "python",
      });

      const completionNames = completions.map((c) => c.label);
      const matches = expected.filter((e) =>
        completionNames.some((n) => n.toLowerCase().includes(e.toLowerCase()))
      );

      if (matches.length > 0) {
        correctPredictions++;
      }
    });

    const accuracy = correctPredictions / testCases.length;
    expect(accuracy).toBeGreaterThanOrEqual(0.9);
  });
});
