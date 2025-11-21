"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layouts/ProtectedRoute";
import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/hooks/use-toast";
import { generateExam } from "@/lib/api/exams";
import { getPDFs } from "@/lib/api/pdfs";
import { PDF, ExamGenerationRequest } from "@/types/api";
import { ArrowLeft, Loader2, FileText } from "lucide-react";
import { LoadingSpinner } from "@/components/ui/loading-spinner";

export default function GenerateExamPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const subjectId = params.subjectId as string;
  const pdfId = params.pdfId as string;

  const [loading, setLoading] = useState(false);
  const [pdfsLoading, setPdfsLoading] = useState(true);
  const [pdfs, setPdfs] = useState<PDF[]>([]);
  const [selectedPdfIds, setSelectedPdfIds] = useState<string[]>([]);
  const [formData, setFormData] = useState({
    num_questions: 5,
    difficulty: "medium" as "easy" | "medium" | "hard",
  });

  useEffect(() => {
    loadPDFs();
  }, [subjectId]);

  useEffect(() => {
    // URL에서 받은 pdfId를 미리 선택
    if (pdfs.length > 0 && pdfId && selectedPdfIds.length === 0) {
      const pdfExists = pdfs.some((pdf) => pdf.file_id === pdfId);
      if (pdfExists) {
        setSelectedPdfIds([pdfId]);
      }
    }
  }, [pdfs, pdfId]);

  const loadPDFs = async () => {
    try {
      const pdfsData = await getPDFs(subjectId);
      setPdfs(pdfsData);
    } catch (error: any) {
      toast({
        title: "PDF 목록 로드 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setPdfsLoading(false);
    }
  };

  const handlePdfToggle = (pdfId: string) => {
    setSelectedPdfIds((prev) =>
      prev.includes(pdfId)
        ? prev.filter((id) => id !== pdfId)
        : [...prev, pdfId]
    );
  };

  const handleSelectAll = () => {
    if (selectedPdfIds.length === pdfs.length) {
      // 최소 하나는 선택되어야 하므로, URL에서 받은 pdfId만 남김
      setSelectedPdfIds(pdfId ? [pdfId] : []);
    } else {
      setSelectedPdfIds(pdfs.map((pdf) => pdf.file_id));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedPdfIds.length === 0) {
      toast({
        title: "PDF 선택 필요",
        description: "최소 1개의 PDF를 선택해주세요.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);

    try {
      // 다중 PDF 지원: pdf_ids 배열 사용
      const request: ExamGenerationRequest = {
        pdf_ids: selectedPdfIds,
        num_questions: formData.num_questions,
        difficulty: formData.difficulty,
      };

      const exam = await generateExam(subjectId, request);
      toast({
        title: "시험 생성 완료",
        description: "AI가 시험을 성공적으로 생성했습니다.",
      });
      router.push(`/dashboard/subjects/${subjectId}/exams/${exam.exam_id}`);
    } catch (error: any) {
      toast({
        title: "시험 생성 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (pdfsLoading) {
    return (
      <ProtectedRoute>
        <AppLayout>
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        </AppLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <AppLayout>
        <div className="mx-auto max-w-3xl space-y-6">
          {/* Header */}
          <div>
            <Link href={`/dashboard/subjects/${subjectId}`}>
              <Button variant="ghost" className="mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" />
                돌아가기
              </Button>
            </Link>
            <h1 className="text-3xl font-bold">시험 생성</h1>
            <p className="mt-2 text-gray-600">
              AI가 PDF를 분석하여 자동으로 시험 문제를 생성합니다
            </p>
          </div>

          {/* PDF Selection */}
          <Card className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label className="text-base font-semibold">PDF 선택</Label>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleSelectAll}
                    disabled={loading || pdfs.length === 0}
                  >
                    {selectedPdfIds.length === pdfs.length
                      ? "전체 해제"
                      : "전체 선택"}
                  </Button>
                </div>

                {pdfs.length === 0 ? (
                  <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center">
                    <FileText className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-4 text-sm font-semibold text-gray-900">
                      업로드된 PDF가 없습니다
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      먼저 PDF를 업로드해주세요.
                    </p>
                    <Link href={`/dashboard/subjects/${subjectId}`}>
                      <Button className="mt-4" variant="outline">
                        과목 페이지로 이동
                      </Button>
                    </Link>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {pdfs.map((pdf) => (
                      <div
                        key={pdf.file_id}
                        className={`flex items-start gap-3 rounded-lg border p-4 transition-all ${
                          selectedPdfIds.includes(pdf.file_id)
                            ? "border-emerald-500 bg-emerald-50"
                            : "border-gray-200 hover:bg-gray-50"
                        }`}
                      >
                        <Checkbox
                          id={pdf.file_id}
                          checked={selectedPdfIds.includes(pdf.file_id)}
                          onCheckedChange={() => handlePdfToggle(pdf.file_id)}
                          disabled={loading}
                          className="mt-1"
                        />
                        <label
                          htmlFor={pdf.file_id}
                          className="flex-1 cursor-pointer"
                        >
                          <div className="font-medium text-gray-900">
                            {pdf.original_filename}
                          </div>
                          <div className="mt-1 text-xs text-gray-500">
                            {(pdf.size / 1024 / 1024).toFixed(2)} MB •{" "}
                            {new Date(pdf.uploaded_at).toLocaleDateString(
                              "ko-KR"
                            )}
                          </div>
                        </label>
                      </div>
                    ))}
                  </div>
                )}

                <p className="text-sm text-gray-500">
                  ✨ <strong>{selectedPdfIds.length}개</strong>의 PDF 선택됨
                  {selectedPdfIds.length > 1 && (
                    <span className="text-emerald-600">
                      {" "}
                      (여러 PDF의 내용을 종합하여 시험이 생성됩니다)
                    </span>
                  )}
                </p>
              </div>
            </Card>

            {/* Exam Options */}
            <Card className="p-6">
              <div className="space-y-6">
                {/* Number of Questions */}
                <div>
                  <Label>문제 수</Label>
                  <div className="mt-2 flex gap-3">
                    {[5, 10, 20].map((num) => (
                      <Button
                        key={num}
                        type="button"
                        variant={formData.num_questions === num ? "default" : "outline"}
                        className={`flex-1 ${
                          formData.num_questions === num
                            ? "bg-emerald-600 hover:bg-emerald-700"
                            : ""
                        }`}
                        onClick={() =>
                          setFormData({ ...formData, num_questions: num })
                        }
                        disabled={loading}
                      >
                        {num}문제
                      </Button>
                    ))}
                  </div>
                </div>

                {/* Difficulty */}
                <div>
                  <Label>난이도</Label>
                  <div className="mt-2 flex gap-3">
                    {[
                      { value: "easy", label: "쉬움" },
                      { value: "medium", label: "보통" },
                      { value: "hard", label: "어려움" },
                    ].map((diff) => (
                      <Button
                        key={diff.value}
                        type="button"
                        variant={
                          formData.difficulty === diff.value ? "default" : "outline"
                        }
                        className={`flex-1 ${
                          formData.difficulty === diff.value
                            ? "bg-emerald-600 hover:bg-emerald-700"
                            : ""
                        }`}
                        onClick={() =>
                          setFormData({
                            ...formData,
                            difficulty: diff.value as "easy" | "medium" | "hard",
                          })
                        }
                        disabled={loading}
                      >
                        {diff.label}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            </Card>

            {/* Estimated Time */}
            <div className="rounded-lg bg-emerald-50 p-4">
              <p className="text-sm text-emerald-900">
                <strong>⚡ 예상 소요 시간:</strong>{" "}
                {formData.num_questions === 5
                  ? "약 1분"
                  : formData.num_questions === 10
                  ? "약 3분"
                  : "약 5분"}
              </p>
              <p className="mt-1 text-xs text-emerald-700">
                AI가 PDF를 빠르게 분석하고 문제를 생성합니다.
              </p>
            </div>

            {/* Actions */}
            <form onSubmit={handleSubmit}>
              <Button
                type="submit"
                disabled={loading || selectedPdfIds.length === 0}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    생성 중... (잠시만 기다려주세요)
                  </>
                ) : (
                  "시험 생성"
                )}
              </Button>
            </form>

          {/* Info */}
          <Card className="p-6">
            <h3 className="font-semibold">💡 팁</h3>
            <ul className="mt-2 space-y-2 text-sm text-gray-600">
              <li>• PDF 내용이 많을수록 더 다양한 문제가 생성됩니다</li>
              <li>• 난이도에 따라 문제의 복잡도가 조정됩니다</li>
              <li>• 객관식과 주관식 문제가 자동으로 생성됩니다</li>
            </ul>
          </Card>
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}
