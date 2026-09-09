import { useEffect, useState } from "react";
import { getFileTree } from "../services/api";
import type { FileTreeNode } from "../types";
import { useSelectedFirmware } from "../hooks/useSelectedFirmware";

function TreeNode({
  node,
  selectedPath,
  onSelect,
  depth,
}: {
  node: FileTreeNode;
  selectedPath: string | null;
  onSelect: (node: FileTreeNode) => void;
  depth: number;
}) {
  const [expanded, setExpanded] = useState(depth < 2);
  const icon = node.is_directory ? (expanded ? "📂" : "📁") : "📄";

  return (
    <div>
      <div
        className={`tree-node${selectedPath === node.path ? " selected" : ""}`}
        onClick={() => {
          if (node.is_directory) setExpanded((prev) => !prev);
          onSelect(node);
        }}
      >
        {icon} {node.name}
      </div>
      {node.is_directory && expanded && node.children.length > 0 && (
        <div className="tree-children">
          {node.children.map((child) => (
            <TreeNode key={child.path} node={child} selectedPath={selectedPath} onSelect={onSelect} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function FilesystemExplorer() {
  const { selectedFirmwareId } = useSelectedFirmware();
  const [tree, setTree] = useState<FileTreeNode | null>(null);
  const [selectedNode, setSelectedNode] = useState<FileTreeNode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedFirmwareId) return;
    setLoading(true);
    setError(null);
    getFileTree(selectedFirmwareId)
      .then(setTree)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load filesystem"))
      .finally(() => setLoading(false));
  }, [selectedFirmwareId]);

  return (
    <div>
      <div className="page-header">
        <h1>Filesystem Explorer</h1>
        <p>Browse the extracted firmware filesystem tree</p>
      </div>

      {!selectedFirmwareId ? (
        <div className="panel">
          <div className="empty-state">
            No firmware selected. Go to Firmware Analysis and select a firmware first.
          </div>
        </div>
      ) : loading ? (
        <div className="panel">
          <div className="empty-state">Loading filesystem...</div>
        </div>
      ) : error ? (
        <div className="panel">
          <div className="empty-state">{error} — Try running Extract on this firmware first.</div>
        </div>
      ) : (
        <div className="two-col">
          <div className="panel">
            <div className="panel-title">Filesystem Tree</div>
            {tree && <div className="tree"><TreeNode node={tree} selectedPath={selectedNode?.path ?? null} onSelect={setSelectedNode} depth={0} /></div>}
          </div>
          <div className="panel">
            <div className="panel-title">File Details</div>
            {selectedNode ? (
              <div>
                <div style={{ marginBottom: 10 }}>
                  <span className="field-label">Path</span>
                  <span className="field-value">/{selectedNode.path}</span>
                </div>
                <div style={{ marginBottom: 10 }}>
                  <span className="field-label">Type</span>
                  <span className="field-value">{selectedNode.is_directory ? "Directory" : "File"}</span>
                </div>
                <div style={{ marginBottom: 10 }}>
                  <span className="field-label">Size</span>
                  <span className="field-value">{selectedNode.size_bytes} bytes</span>
                </div>
              </div>
            ) : (
              <div className="empty-state">Select a file or directory from the tree</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
