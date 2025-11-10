import { useState } from "react";
import { Card } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Upload } from "lucide-react";

interface PDFUploadZoneProps {
  onFileUpload: (file: File) => void;
  uploading: boolean;
}

export function PDFUploadZone({ onFileUpload, uploading }: PDFUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      onFileUpload(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileUpload(file);
      e.target.value = "";
    }
  };

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">PDF 자료</h2>
            <p className="mt-1 text-sm text-gray-600">
              강의 자료를 업로드하여 시험을 생성하세요
            </p>
          </div>
        </div>

        {/* Drag and Drop Area */}
        <div
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => document.getElementById("pdf-upload")?.click()}
          className={`
            relative border-2 border-dashed rounded-lg p-12 
            text-center cursor-pointer transition-colors
            ${
              isDragging
                ? "border-emerald-500 bg-emerald-50"
                : "border-gray-300 hover:border-gray-400 bg-gray-50"
            }
            ${uploading ? "opacity-50 cursor-not-allowed" : ""}
          `}
        >
          <input
            type="file"
            id="pdf-upload"
            accept=".pdf"
            onChange={handleFileInput}
            className="hidden"
            disabled={uploading}
          />

          <div className="flex flex-col items-center justify-center gap-4">
            {uploading ? (
              <>
                <LoadingSpinner size="lg" />
                <p className="text-lg font-medium text-gray-700">업로드 중...</p>
              </>
            ) : (
              <>
                <Upload
                  className={`h-12 w-12 ${
                    isDragging ? "text-emerald-500" : "text-gray-400"
                  }`}
                />
                <div>
                  <p className="text-lg font-medium text-gray-700">
                    {isDragging
                      ? "PDF 파일을 여기에 놓으세요"
                      : "PDF 파일을 드래그하거나 클릭하여 업로드"}
                  </p>
                  <p className="mt-1 text-sm text-gray-500">
                    최대 16MB까지 업로드 가능
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}

