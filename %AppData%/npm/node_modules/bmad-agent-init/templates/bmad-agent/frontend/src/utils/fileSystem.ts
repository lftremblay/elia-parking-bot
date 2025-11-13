// Using the browser's built-in fetch API

// Get API base URL from environment variable or use default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';

export interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  children?: FileNode[];
}

export async function readProjectDirectory(dirPath: string): Promise<FileNode> {
  try {
    // Ensure the path is properly encoded and doesn't have leading/trailing slashes
    let cleanPath = dirPath.replace(/^\/+|\/+$/g, '');
    // If the path doesn't start with 'docs', prepend it
    if (!cleanPath.startsWith('docs')) {
      cleanPath = `docs${cleanPath ? '/' + cleanPath : ''}`;
    }
    const apiUrl = `${API_BASE_URL}/files?path=${encodeURIComponent(cleanPath)}`;
    console.log('Fetching directory:', apiUrl);
    
    const response = await fetch(apiUrl);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Failed to read directory: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error reading directory:', error);
    throw error instanceof Error ? error : new Error('Failed to read directory');
  }
}

export async function readFileContent(filePath: string): Promise<string> {
  try {
    // Ensure the path is properly encoded and doesn't have leading/trailing slashes
    let cleanPath = filePath.replace(/^\/+|\/+$/g, '');
    // If the path doesn't start with 'docs', prepend it
    if (!cleanPath.startsWith('docs')) {
      cleanPath = `docs${cleanPath ? '/' + cleanPath : ''}`;
    }
    const apiUrl = `${API_BASE_URL}/files/content?path=${encodeURIComponent(cleanPath)}`;
    console.log('Fetching file content:', apiUrl);
    
    const response = await fetch(apiUrl);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Failed to read file: ${response.statusText}`);
    }
    
    return await response.text();
  } catch (error) {
    console.error('Error reading file:', error);
    throw error instanceof Error ? error : new Error('Failed to read file');
  }
}
