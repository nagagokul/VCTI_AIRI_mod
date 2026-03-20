import { useRef, useState } from "react";

interface Props {
  files: File[];
  setFiles: (files: File[]) => void;
}

export default function ResumeUpload({ files, setFiles }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFiles = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return;

    const newFiles = Array.from(selectedFiles);
    setFiles([...files, ...newFiles]);
  };

  const removeFile = (index: number) => {
    const updated = files.filter((_, i) => i !== index);
    setFiles(updated);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div className="space-y-4">
      <div
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition ${
          isDragOver ? 'border-blue-500 bg-blue-500/10' : 'border-slate-700 hover:border-blue-500'
        }`}
      >
        <p className="text-slate-300">Drag & Drop resumes here</p>

        <p className="text-sm text-slate-500 mt-1">or click to upload</p>

        <input
          type="file"
          multiple
          accept=".pdf,.doc,.docx"
          ref={fileInputRef}
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm text-slate-400">Uploaded Files</h3>

          {files.map((file, index) => (
            <div
              key={index}
              className="flex justify-between items-center bg-slate-900 border border-slate-800 rounded p-3"
            >
              <span className="text-sm">{file.name}</span>

              <button
                onClick={() => removeFile(index)}
                className="text-red-400 text-xs"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
