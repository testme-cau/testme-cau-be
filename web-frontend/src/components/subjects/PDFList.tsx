import { PDF } from "@/types/api";
import { EmptyState } from "@/components/ui/empty-state";
import { PDFItem } from "./PDFItem";
import { FileText } from "lucide-react";

interface PDFListProps {
  pdfs: PDF[];
  subjectId: string;
  onDownload: (pdfId: string) => void;
  onDelete: (pdf: PDF) => void;
}

export function PDFList({ pdfs, subjectId, onDownload, onDelete }: PDFListProps) {
  if (!pdfs || pdfs.length === 0) {
    return (
      <EmptyState
        icon={<FileText className="h-12 w-12" />}
        title="업로드된 PDF가 없습니다"
        description="PDF 자료를 업로드하여 시작하세요"
      />
    );
  }

  return (
    <div className="space-y-3">
      {pdfs.map((pdf) => (
        <PDFItem
          key={pdf.file_id}
          pdf={pdf}
          subjectId={subjectId}
          onDownload={onDownload}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}

