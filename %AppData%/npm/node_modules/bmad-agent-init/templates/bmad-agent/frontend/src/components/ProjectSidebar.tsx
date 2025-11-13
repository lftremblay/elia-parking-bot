import { useState, useEffect } from "react";
import { Plus, Search, Folder } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { readProjectDirectory, FileNode } from "@/utils/fileSystem";
import { FileTree } from "./FileTree";
import { useExpandedDirectories } from "@/hooks/useExpandedDirectories";

// Browser-compatible path joining
const joinPaths = (...parts: string[]): string => {
  return parts
    .map((part, i) => {
      if (i === 0) {
        return part.trim().replace(/[/]*$/g, '');
      } else {
        return part.trim().replace(/(^[/]*|[/]*$)/g, '');
      }
    })
    .filter(part => part.length > 0)
    .join('/');
};

interface ProjectSidebarProps {
  selectedProject: string | null;
  onSelectProject: (project: string) => void;
  selectedFile: string | null;
  onSelectFile: (file: string) => void;
  collapsed: boolean;
}

export const ProjectSidebar = ({
  selectedProject,
  onSelectProject,
  selectedFile,
  onSelectFile,
  collapsed
}: ProjectSidebarProps) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [fileTree, setFileTree] = useState<FileNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { expandedDirs, toggleDir } = useExpandedDirectories();

  // Load the file tree when the component mounts
  useEffect(() => {
    const loadFileTree = async () => {
      try {
        setLoading(true);
        // Read from the project root (one level up from the frontend directory)
        const rootPath = joinPaths(import.meta.env.VITE_APP_PROJECT_ROOT || '..');
        const tree = await readProjectDirectory(rootPath);
        setFileTree(tree);
      } catch (err) {
        console.error('Error loading file tree:', err);
        setError('Failed to load project files');
      } finally {
        setLoading(false);
      }
    };

    loadFileTree();
  }, []);

  // If collapsed, only show the toggle button
  if (collapsed) {
    return (
      <div className="w-12 h-full border-r border-gray-200 bg-white flex flex-col items-center py-4">
        <Button
          variant="ghost"
          size="icon"
          className="w-8 h-8 rounded-full bg-blue-50 text-blue-600"
        >
          <span className="text-xs font-medium">BM</span>
        </Button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="w-80 h-full border-r border-gray-200 bg-white flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">BMAD Agent</h2>
          </div>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" />
            <Input
              className="pl-8"
              placeholder="Search files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        <div className="flex-1 overflow-auto p-2">
          <div className="text-center py-8 text-gray-500">
            Loading project files...
          </div>
        </div>
        <div className="p-3 border-t border-gray-200 bg-gray-50 text-xs text-gray-500">
          {fileTree?.path || 'Project root'}
        </div>
      </div>
    );
  }

  return (
    <div className="w-80 h-full border-r border-gray-200 bg-white flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">BMAD Agent</h2>
        </div>
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" />
          <Input
            className="pl-8"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>
      
      <div className="flex-1 overflow-auto p-2">
        {fileTree?.children?.map((child) => (
          <FileTree
            key={child.path}
            node={child}
            selectedFile={selectedFile}
            onSelectFile={onSelectFile}
            expandedDirs={expandedDirs}
            onToggleDir={toggleDir}
          />
        ))}
      </div>
      
      <div className="p-3 border-t border-gray-200 bg-gray-50 text-xs text-gray-500">
        {fileTree?.path || 'Project root'}
      </div>
    </div>
  );
};
