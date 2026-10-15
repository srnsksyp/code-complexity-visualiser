"use client";

import React, { useRef } from "react";
import Editor, { OnMount } from "@monaco-editor/react";
import { Play, RotateCcw, Code2, Sparkles, BookOpen } from "lucide-react";
import { CODE_EXAMPLES, CodeExample } from "@/lib/examples";

interface CodeEditorProps {
  code: string;
  onChange: (value: string) => void;
  onAnalyze: () => void;
  isLoading: boolean;
  onSelectExample: (example: CodeExample) => void;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  onChange,
  onAnalyze,
  isLoading,
  onSelectExample,
}) => {
  const editorRef = useRef<any>(null);

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    // Add keyboard shortcut: Ctrl+Enter or Cmd+Enter to run analysis
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      onAnalyze();
    });
  };

  const handleReset = () => {
    onChange("");
    if (editorRef.current) {
      editorRef.current.focus();
    }
  };

  const lineCount = code.split("\n").length;
  const charCount = code.length;

  return (
    <div className="flex flex-col h-full bg-[#18181b] border border-zinc-800 rounded-xl overflow-hidden shadow-2xl">
      {/* Editor Header Toolbar */}
      <div className="flex flex-wrap items-center justify-between px-4 py-2.5 bg-zinc-900 border-b border-zinc-800 gap-2">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-zinc-300 font-medium text-sm">
            <Code2 className="w-4 h-4 text-emerald-400" />
            <span>Python Source</span>
          </div>

          {/* Example presets selector */}
          <div className="relative inline-flex items-center">
            <BookOpen className="w-3.5 h-3.5 text-zinc-400 absolute left-2.5 pointer-events-none" />
            <select
              aria-label="Load code example preset"
              onChange={(e) => {
                const ex = CODE_EXAMPLES.find((item) => item.id === e.target.value);
                if (ex) onSelectExample(ex);
              }}
              defaultValue=""
              className="bg-zinc-800 text-zinc-200 text-xs rounded-lg pl-8 pr-3 py-1.5 border border-zinc-700 hover:border-zinc-600 focus:outline-none focus:ring-1 focus:ring-emerald-500 cursor-pointer"
            >
              <option value="" disabled>
                Load Example Algorithm...
              </option>
              {CODE_EXAMPLES.map((ex) => (
                <option key={ex.id} value={ex.id}>
                  {ex.name} ({ex.expectedTime})
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            disabled={isLoading || !code}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-zinc-400 hover:text-zinc-200 bg-zinc-800/80 hover:bg-zinc-800 border border-zinc-700/60 rounded-lg transition disabled:opacity-40 disabled:cursor-not-allowed"
            title="Clear Editor"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>

          <button
            onClick={onAnalyze}
            disabled={isLoading || !code.trim()}
            className="flex items-center gap-2 px-4 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 active:scale-95 transition rounded-lg shadow-lg shadow-emerald-950/40 disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100"
          >
            {isLoading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Analyzing AST...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Analyze Code</span>
                <span className="hidden sm:inline text-[10px] text-emerald-200/70 border border-emerald-400/30 px-1 rounded">
                  Ctrl+Enter
                </span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Monaco Editor Container */}
      <div className="flex-1 min-h-[380px] relative">
        <Editor
          height="100%"
          language="python"
          theme="vs-dark"
          value={code}
          onChange={(val) => onChange(val || "")}
          onMount={handleEditorDidMount}
          options={{
            minimap: { enabled: false },
            fontSize: 13.5,
            fontFamily: "JetBrains Mono, Menlo, Monaco, 'Courier New', monospace",
            lineNumbers: "on",
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
            padding: { top: 12, bottom: 12 },
            renderLineHighlight: "all",
            cursorBlinking: "smooth",
            smoothScrolling: true,
            wordWrap: "on",
          }}
        />
      </div>

      {/* Editor Footer Status */}
      <div className="flex items-center justify-between px-4 py-1.5 bg-zinc-900/90 border-t border-zinc-800 text-[11px] text-zinc-400 font-mono">
        <div className="flex items-center gap-3">
          <span>Python 3.x AST</span>
          <span>•</span>
          <span>Deterministic Static Engine</span>
        </div>
        <div className="flex items-center gap-3">
          <span>{lineCount} lines</span>
          <span>{charCount} chars</span>
        </div>
      </div>
    </div>
  );
};
