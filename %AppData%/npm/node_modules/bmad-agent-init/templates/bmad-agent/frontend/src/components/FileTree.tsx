import { FileNode } from "@/utils/fileSystem";
import { ChevronDown, ChevronRight, Folder, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

interface FileTreeProps {
  node: FileNode;
  level?: number;
  selectedFile: string | null;
  onSelectFile: (path: string) => void;
  expandedDirs: Set<string>;
  onToggleDir: (path: string) => void;
}

export function FileTree({
  node,
  level = 0,
  selectedFile,
  onSelectFile,
  expandedDirs,
  onToggleDir,
}: FileTreeProps) {
  const isExpanded = expandedDirs.has(node.path);
  const isDir = node.type === 'directory';
  const hasChildren = isDir && node.children && node.children.length > 0;
  const isBmadAgentDir = node.name === 'bmad-agent';

  return (
    <div className="select-none">
      <div
        className={cn(
          "flex items-center py-1 px-2 rounded-md cursor-pointer hover:bg-gray-100",
          selectedFile === node.path && "bg-blue-50 text-blue-600",
          level === 0 ? "font-medium" : ""
        )}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={() => isDir ? onToggleDir(node.path) : onSelectFile(node.path)}
      >
        {isDir ? (
          <>
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 mr-1 text-gray-500" />
            ) : (
              <ChevronRight className="h-4 w-4 mr-1 text-gray-500" />
            )}
            <Folder className="h-4 w-4 mr-2 text-blue-500" />
          </>
        ) : (
          <FileText className="h-4 w-4 mr-2 text-gray-500" />
        )}
        <span className="truncate">{node.name}</span>
      </div>
      
      {isExpanded && hasChildren && node.children && (
        <div>
          {node.children.map(child => (
            <FileTree
              key={child.path}
              node={child}
              level={level + 1}
              selectedFile={selectedFile}
              onSelectFile={onSelectFile}
              expandedDirs={expandedDirs}
              onToggleDir={onToggleDir}
            />
          ))}
        </div>
      )}
    </div>
  );
}
