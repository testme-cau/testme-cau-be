import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PDF } from "@/types/api";
import { FileText, Download, Trash2, ClipboardList } from "lucide-react";

interface PDFItemProps {
  pdf: PDF;
  subjectId: string;
  onDownload: (pdfId: string) => void;
  onDelete: (pdf: PDF) => void;
}

export function PDFItem({ pdf, subjectId, onDownload, onDelete }: PDFItemProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  return (
    <Card key={pdf.file_id} className="p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText className="h-8 w-8 text-gray-400" />
          <div>
            <h3 className="font-medium">{pdf.original_filename}</h3>
            <p className="text-sm text-gray-500">
              {formatFileSize(pdf.size)} •{" "}
              {new Date(pdf.uploaded_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Link
            href={`/dashboard/subjects/${subjectId}/pdfs/${pdf.file_id}/generate-exam`}
          >
            <Button size="sm">
              <ClipboardList className="mr-2 h-4 w-4" />
              시험 생성
            </Button>
          </Link>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onDownload(pdf.file_id)}
          >
            <Download className="h-4 w-4" />
          </Button>
          <Button size="sm" variant="outline" onClick={() => onDelete(pdf)}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
}

