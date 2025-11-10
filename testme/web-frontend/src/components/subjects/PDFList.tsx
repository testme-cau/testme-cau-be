import { useState, useEffect } from "react";
import { PDF } from "@/types/api";
import { EmptyState } from "@/components/ui/empty-state";
import { PDFItem } from "./PDFItem";
import { FileText } from "lucide-react";
import { getPDFs, downloadPDF, deletePDF } from "@/lib/api/pdfs";
import { useToast } from "@/hooks/use-toast";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";

interface PDFListProps {
  subjectId: string;
  initialPdfs: PDF[];
}

export function PDFList({ subjectId, initialPdfs }: PDFListProps) {
  const [pdfs, setPdfs] = useState<PDF[]>(initialPdfs);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [pdfToDelete, setPdfToDelete] = useState<PDF | null>(null);
  const [deleting, setDeleting] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    setPdfs(initialPdfs);
  }, [initialPdfs]);

  const handleDownload = async (pdfId: string) => {
    try {
      await downloadPDF(subjectId, pdfId);
    } catch (error: any) {
      toast({
        title: "다운로드 실패",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const handleDeleteClick = (pdf: PDF) => {
    setPdfToDelete(pdf);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!pdfToDelete) return;

    setDeleting(true);
    try {
      await deletePDF(subjectId, pdfToDelete.file_id);
      setPdfs((prev) => prev.filter((p) => p.file_id !== pdfToDelete.file_id));
      toast({
        title: "삭제 완료",
        description: "PDF가 삭제되었습니다.",
      });
    } catch (error: any) {
      toast({
        title: "삭제 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setDeleting(false);
      setDeleteDialogOpen(false);
      setPdfToDelete(null);
    }
  };
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
    <>
      <div className="space-y-3">
        {pdfs.map((pdf) => (
          <PDFItem
            key={pdf.file_id}
            pdf={pdf}
            subjectId={subjectId}
            onDownload={handleDownload}
            onDelete={handleDeleteClick}
          />
        ))}
      </div>

      <ConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        title="PDF 삭제"
        description={`정말로 "${pdfToDelete?.original_filename}"을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`}
        onConfirm={handleDeleteConfirm}
        confirmText="삭제"
        cancelText="취소"
        variant="destructive"
        loading={deleting}
      />
    </>
  );
}

